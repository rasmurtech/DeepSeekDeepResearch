from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import List, Optional, Union, Dict
import re  # For cleaning chain-of-thought tokens
import logging
import json
import functools
import aiohttp
import asyncio
import nest_asyncio
nest_asyncio.apply()


# For retries

# For Google Custom Search API

# Optional: For local webpage extraction using Newspaper3k
try:
    from newspaper import Article
    USE_NEWSPAPER = True
except ImportError:
    USE_NEWSPAPER = False

# =======================
# Configuration Constants
# =======================
# Google Custom Search settings
GOOGLE_API_KEY = "Your Key"  # Provided API key
# Provided Custom Search Engine ID
GOOGLE_CX = "Your Key"

# Optional: Jina settings (only used if you do not use Newspaper3k)
JINA_API_KEY = "REDACTED"      # Replace with your Jina API key if desired
JINA_BASE_URL = "https://r.jina.ai/"

# ============================
# Logging Setup
# ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================
# Utility Function to Clean LLM Response
# ============================


def clean_response(response: str) -> str:
    """
    Removes chain-of-thought markers like <think>...</think> and any stray tokens.
    """
    cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    cleaned = cleaned.replace("<think>", "").replace("</think>", "")
    return cleaned.strip()

# ============================
# Helper Functions for Calling Ollama
# ============================


async def async_call_ollama_llm(messages: List[dict]) -> str:
    """
    Combines conversation messages into a single prompt and uses Ollama to run the 
    deepseek-r1:7b model. The command "ollama run deepseek-r1:7b" is executed,
    and the prompt is sent via standard input.
    """
    prompt = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in messages])
    process = await asyncio.create_subprocess_exec(
        "ollama", "run", "deepseek-r1:7b",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate(prompt.encode())
    if process.returncode != 0:
        logger.error("Ollama run error: %s", stderr.decode())
        return ""
    response = stdout.decode().strip()
    return clean_response(response)

# ============================
# Google Custom Search Function
# ============================


def perform_google_search(query: str) -> List[str]:
    """
    Uses the Google Custom Search API to perform a search for the given query.
    Returns a list of result URLs.
    """
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=GOOGLE_CX).execute()
    links = [item["link"] for item in res.get("items", [])]
    return links


async def perform_search_async(query: str) -> List[str]:
    """
    Asynchronously perform a Google search using the Custom Search API.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(perform_google_search, query))

# ============================
# Webpage Extraction
# ============================


async def fetch_webpage_text_async(session: aiohttp.ClientSession, url: str) -> str:
    """
    Asynchronously retrieve the text content of a webpage.
    If USE_NEWSPAPER is True, use Newspaper3k for extraction; otherwise, use the Jina API.
    """
    if url in webpage_cache:
        return webpage_cache[url]
    if USE_NEWSPAPER:
        try:
            loop = asyncio.get_running_loop()

            def fetch_with_newspaper(u: str) -> str:
                article = Article(u)
                article.download()
                article.parse()
                return article.text
            text_content = await loop.run_in_executor(None, fetch_with_newspaper, url)
            webpage_cache[url] = text_content
            return text_content
        except Exception as e:
            logger.exception("Newspaper extraction failed for %s", url)
            return ""
    else:
        full_url = f"{JINA_BASE_URL}{url}"
        headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
        try:
            async with session.get(full_url, headers=headers) as resp:
                if resp.status == 200:
                    text_content = await resp.text()
                    webpage_cache[url] = text_content
                    return text_content
                else:
                    text = await resp.text()
                    logger.error("Jina fetch error for %s: %s - %s",
                                 url, resp.status, text)
                    return ""
        except Exception as e:
            logger.exception(
                "Error fetching webpage text with Jina for %s:", url)
            return ""

# In-memory cache for webpage texts.
webpage_cache: Dict[str, str] = {}

# ============================
# Asynchronous Helper Functions for the Research Loop
# ============================


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def generate_search_queries_async(user_query: str) -> List[str]:
    """
    Ask Ollama (via deepseek-r1:7b) to produce up to four precise search queries based on the user's query.
    The prompt instructs the model to return a JSON array of strings with no extra commentary.
    If the response is empty or invalid, fall back to using the original query.
    """
    prompt = (
        "You are an expert research assistant. Given the user's query, generate up to four distinct, "
        "precise search queries that would help gather comprehensive information on the topic. "
        "Return only a JSON array of strings (for example: [\"query1\", \"query2\", \"query3\"]) without any additional text."
    )
    messages = [
        {"role": "system", "content": "You are a helpful and precise research assistant."},
        {"role": "user", "content": f"User Query: {user_query}\n\n{prompt}"}
    ]
    response = await async_call_ollama_llm(messages)
    if not response.strip():
        logger.error(
            "LLM returned an empty response. Falling back to the original query.")
        return [user_query]
    try:
        search_queries = json.loads(response)
        if isinstance(search_queries, list):
            return search_queries
        else:
            logger.error(
                "LLM did not return a JSON list. Response: %s", response)
            return [user_query]
    except Exception as e:
        logger.exception(
            "Error parsing search queries as JSON. Raw response: %s", response)
        return [user_query]


async def is_page_useful_async(user_query: str, page_text: str) -> str:
    """
    Ask Ollama if the provided webpage content is useful for answering the user's query.
    Expects exactly "Yes" or "No".
    """
    prompt = (
        "You are a critical research evaluator. Given the user's query and the content of a webpage, "
        "determine if the webpage contains information relevant and useful for addressing the query. "
        "Respond with exactly one word: 'Yes' if the page is useful, or 'No' if it is not. Do not include any extra text."
    )
    messages = [
        {"role": "system", "content": "You are a strict and concise evaluator of research relevance."},
        {"role": "user",
            "content": f"User Query: {user_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await async_call_ollama_llm(messages)
    if response:
        answer = response.strip()
        if answer in ["Yes", "No"]:
            return answer
        else:
            if "Yes" in answer:
                return "Yes"
            elif "No" in answer:
                return "No"
    return "No"


async def extract_relevant_context_async(user_query: str, search_query: str, page_text: str) -> str:
    """
    Ask Ollama to extract information from a page that is relevant to answering the user's query.
    """
    prompt = (
        "You are an expert information extractor. Given the user's query, the search query that led to this page, "
        "and the webpage content, extract all pieces of information that are relevant to answering the user's query. "
        "Return only the relevant context as plain text without commentary."
    )
    messages = [
        {"role": "system", "content": "You are an expert in extracting and summarizing relevant information."},
        {"role": "user",
            "content": f"User Query: {user_query}\nSearch Query: {search_query}\n\nWebpage Content (first 20000 characters):\n{page_text[:20000]}\n\n{prompt}"}
    ]
    response = await async_call_ollama_llm(messages)
    if response:
        return response.strip()
    return ""


async def get_new_search_queries_async(user_query: str, previous_search_queries: List[str], all_contexts: List[str]) -> Union[str, List[str]]:
    """
    Ask Ollama whether additional search queries are needed based on the aggregated contexts.
    """
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an analytical research assistant. Based on the original query, the search queries performed so far, "
        "and the extracted contexts from webpages, determine if further research is needed. "
        "If further research is needed, provide up to four new search queries as a JSON array of strings (for example, "
        "[\"new query1\", \"new query2\"]). If you believe no further research is needed, respond with exactly \"<done>\"."
        "\nOutput only a JSON array or the token \"<done>\" without any additional text."
    )
    messages = [
        {"role": "system", "content": "You are a systematic research planner."},
        {"role": "user", "content": f"User Query: {user_query}\nPrevious Search Queries: {previous_search_queries}\n\nExtracted Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    response = await async_call_ollama_llm(messages)
    if response:
        cleaned = response.strip()
        if cleaned == "<done>":
            return "<done>"
        try:
            new_queries = json.loads(cleaned)
            if isinstance(new_queries, list):
                return new_queries
            else:
                logger.error(
                    "LLM did not return a JSON list for new search queries. Response: %s", response)
                return []
        except Exception as e:
            logger.exception(
                "Error parsing new search queries as JSON. Raw response: %s", response)
            return []
    return []


async def generate_final_report_async(user_query: str, all_contexts: List[str]) -> Optional[str]:
    """
    Ask Ollama to generate a comprehensive final report using the aggregated contexts.
    """
    context_combined = "\n".join(all_contexts)
    prompt = (
        "You are an expert researcher and report writer. Based on the gathered contexts below and the original query, "
        "write a comprehensive, well-structured, and detailed report that addresses the query thoroughly. "
        "Include all relevant insights and conclusions without extraneous commentary."
    )
    messages = [
        {"role": "system", "content": "You are a skilled report writer."},
        {"role": "user", "content": f"User Query: {user_query}\n\nGathered Relevant Contexts:\n{context_combined}\n\n{prompt}"}
    ]
    report = await async_call_ollama_llm(messages)
    return report

# ============================
# Link Processing and Batch Helpers
# ============================


async def process_link(session: aiohttp.ClientSession, link: str, user_query: str, search_query: str, semaphore: asyncio.Semaphore) -> Optional[str]:
    """
    Process a single link: fetch its content, evaluate its usefulness, and if useful, extract the relevant context.
    """
    async with semaphore:
        logger.info("Fetching content from: %s", link)
        page_text = await fetch_webpage_text_async(session, link)
        if not page_text:
            return None
        usefulness = await is_page_useful_async(user_query, page_text)
        logger.info("Page usefulness for %s: %s", link, usefulness)
        if usefulness == "Yes":
            context = await extract_relevant_context_async(user_query, search_query, page_text)
            if context:
                logger.info(
                    "Extracted context from %s (first 200 chars): %s", link, context[:200])
                return context
    return None


async def batch_gather(tasks: List[asyncio.Task], batch_size: int = 10) -> List:
    """
    Process tasks in batches to control resource usage.
    """
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        results.extend(await asyncio.gather(*batch))
    return results

# ============================
# Main Asynchronous Routine
# ============================


async def async_main():
    user_query = input("Enter your research query/topic: ").strip()
    iter_limit_input = input(
        "Enter maximum number of iterations (default 10): ").strip()
    iteration_limit = int(
        iter_limit_input) if iter_limit_input.isdigit() else 10

    # All useful contexts from every iteration
    aggregated_contexts: List[str] = []
    # Every search query used across iterations
    all_search_queries: List[str] = []
    iteration = 0

    # Use a TCPConnector for connection pooling
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        # ----- INITIAL SEARCH QUERIES -----
        new_search_queries = await generate_search_queries_async(user_query)
        if not new_search_queries:
            logger.error(
                "No search queries were generated by the LLM. Exiting.")
            return
        all_search_queries.extend(new_search_queries)

        # Define a semaphore for concurrent processing (limit 10 concurrent tasks)
        semaphore = asyncio.Semaphore(10)

        # ----- ITERATIVE RESEARCH LOOP -----
        while iteration < iteration_limit:
            logger.info("\n=== Iteration %s ===", iteration + 1)
            iteration_contexts: List[str] = []

            # For each search query, perform Google searches concurrently.
            search_tasks = [perform_search_async(
                query) for query in new_search_queries]
            search_results = await asyncio.gather(*search_tasks)

            # Aggregate all unique links from this iteration, mapping each link to its originating query.
            unique_links: Dict[str, str] = {}
            for idx, links in enumerate(search_results):
                query = new_search_queries[idx]
                for link in links:
                    if link not in unique_links:
                        unique_links[link] = query

            logger.info(
                "Aggregated %s unique links from this iteration.", len(unique_links))

            # Process each link concurrently: fetch, evaluate, and extract context.
            link_tasks = [
                process_link(session, link, user_query,
                             unique_links[link], semaphore)
                for link in unique_links
            ]
            link_results = await batch_gather(link_tasks, batch_size=10)

            # Collect non-None contexts.
            for res in link_results:
                if res:
                    iteration_contexts.append(res)

            if iteration_contexts:
                aggregated_contexts.extend(iteration_contexts)
            else:
                logger.info("No useful contexts were found in this iteration.")

            # ----- ASK THE LLM IF MORE SEARCHES ARE NEEDED -----
            new_search_queries_or_done = await get_new_search_queries_async(user_query, all_search_queries, aggregated_contexts)
            if new_search_queries_or_done == "<done>":
                logger.info(
                    "LLM indicated that no further research is needed.")
                break
            elif isinstance(new_search_queries_or_done, list) and new_search_queries_or_done:
                logger.info("LLM provided new search queries: %s",
                            new_search_queries_or_done)
                all_search_queries.extend(new_search_queries_or_done)
                new_search_queries = new_search_queries_or_done
            else:
                logger.info(
                    "LLM did not provide any new search queries. Ending the loop.")
                break

            iteration += 1

        # ----- FINAL REPORT -----
        logger.info("\nGenerating final report...")
        final_report = await generate_final_report_async(user_query, aggregated_contexts)
        logger.info("\n==== FINAL REPORT ====\n")
        print(final_report)

        # Write the final report to a text file in the same directory.
        try:
            with open("final_report.txt", "w", encoding="utf-8") as f:
                f.write(final_report)
            logger.info("Final report saved to final_report.txt")
        except Exception as e:
            logger.exception("Error writing final report to file.")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
