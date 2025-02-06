
Local Deep Researcher is a Python-based AI research assistant that continuously searches for and extracts relevant information from the web based on a user query. It leverages a local LLM (DeepSeek-R1:7b via Ollama), the Google Custom Search API for search queries, and asynchronous webpage extraction (using Newspaper3k or a fallback to Jina) to generate a comprehensive, detailed report on a given topic. When the research process is complete, the final report is saved as a text file (`final_report.txt`) in the repository directory.

## Features

- **Iterative Research Loop:**  
  Continuously refines search queries and gathers context until no additional queries are needed.

- **Asynchronous Processing:**  
  Performs searches, webpage fetching, and context extraction concurrently for improved speed.

- **Local LLM-Powered Decision Making:**  
  Uses Ollama to call the DeepSeek-R1:7b model locally for:
  - Generating precise search queries
  - Evaluating webpage usefulness
  - Extracting relevant context from webpages
  - Producing a final comprehensive report

- **Google Custom Search Integration:**  
  Uses the Google Custom Search JSON API to retrieve relevant links for each generated query.

- **Webpage Extraction:**  
  Extracts webpage content using Newspaper3k (with a fallback to Jina if Newspaper3k is unavailable).

- **Duplicate Filtering:**  
  Aggregates and deduplicates links across search rounds to ensure efficiency.

- **Final Report Generation and Saving:**  
  Compiles all extracted information into a detailed final report and saves it as `final_report.txt` in the same directory as the Python file.

## Requirements

- **Python 3.8+**
- **Ollama** installed and available in your system PATH  
  (Ensure that running `ollama run deepseek-r1:7b` in your terminal works as expected.)
- **Google Custom Search API Key** and **Custom Search Engine ID**  
  (These are required to perform web searches.)
- **Optional:**  
  - Newspaper3k (for local webpage extraction)  
    Install with: `pip install newspaper3k`  
  - Jina API credentials (if you prefer using Jina as a fallback for webpage extraction)
- **Other Dependencies:**  
  - nest_asyncio  
  - aiohttp  
  - tenacity  
  - google-api-python-client

Install the Python dependencies using pip:

```bash
pip install nest_asyncio aiohttp tenacity google-api-python-client newspaper3k
