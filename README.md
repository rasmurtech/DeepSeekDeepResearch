# DeepSeek Deep Research

DeepSeekDeepResearch is a Python-based AI research assistant that continuously searches for and extracts relevant information from the web based on a user query. It leverages a local LLM (**DeepSeek-R1:7b via Ollama**), the **Google Custom Search API** for search queries, and asynchronous webpage extraction (**Newspaper3k** or **Jina**) to generate a comprehensive, detailed report on a given topic.

The final report is saved as `final_report.txt` in the repository directory upon completion.

## Features

- **Iterative Research Loop** - Continuously refines search queries and gathers context until no additional queries are needed.
- **Asynchronous Processing** - Performs searches, webpage fetching, and context extraction concurrently for improved speed.
- **Local LLM-Powered Decision Making** - Uses **DeepSeek-R1:7b** via **Ollama** to:
  - Generate precise search queries
  - Evaluate webpage usefulness
  - Extract relevant context from webpages
  - Produce a final comprehensive report
- **Google Custom Search Integration** - Uses the **Google Custom Search JSON API** to retrieve relevant links for each generated query.
- **Webpage Extraction** - Extracts webpage content using **Newspaper3k** (with **Jina** as a fallback if needed).
- **Duplicate Filtering** - Aggregates and deduplicates links across search rounds to ensure efficiency.
- **Final Report Generation and Saving** - Compiles all extracted information into a detailed final report and saves it as `final_report.txt`.

---

## Setup

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/local-deep-researcher.git
cd local-deep-researcher
```

### 2. Configure API Keys

- Open the `main.py` file.
- Replace the placeholders for `GOOGLE_API_KEY` and `GOOGLE_CX` with your actual **Google API Key** and **Custom Search Engine ID**.
- If using **Jina** for webpage extraction, update `JINA_API_KEY` and `JINA_BASE_URL` as needed.

### 3. Ensure Ollama is Installed

Verify that Ollama is installed on your system and that the following command runs without errors:

```bash
ollama run deepseek-r1:7b
```

### 4. Install Dependencies

Ensure you have **Python 3.8+** and install the required dependencies:

```bash
pip install nest_asyncio aiohttp tenacity google-api-python-client newspaper3k
```

---

## Usage

### Run the Program

Execute the script from your terminal:

```bash
python main.py
```

### Input Prompt
- **Research Query/Topic:** Enter a research query or topic (e.g., *"What is UAP?"*).
- **Maximum Number of Iterations:** Optionally, specify the max iterations (default is **10**).

### Research Process
1. **Initial Query & Search Generation:**
   - The local **LLM (DeepSeek-R1:7b via Ollama)** generates up to **four distinct** search queries based on your input.

2. **Concurrent Search & Extraction:**
   - Each query is sent to the **Google Custom Search API**.
   - The program aggregates, deduplicates links, and fetches webpage content **asynchronously**.

3. **Evaluation & Context Extraction:**
   - The **LLM** evaluates webpage relevance and extracts useful context.

4. **Iterative Refinement:**
   - The **LLM** determines if additional search queries are needed.
   - The process repeats until:
     - The iteration limit is reached, or
     - No new queries are generated.

5. **Final Report Generation & Saving:**
   - A **detailed final report** is compiled, printed to the console, and saved as `final_report.txt`.

---

## How It Works

### 1. Input & Query Generation
- The **LLM** processes the user’s query and generates up to **four** distinct search queries.

### 2. Concurrent Google Searches
- Each query is sent **concurrently** to the **Google Custom Search API**.
- The returned links are **aggregated and deduplicated**.

### 3. Webpage Processing
For each **unique** link:
- **Content Extraction** → Extracted using **Newspaper3k** (or **Jina** as a fallback).
- **Usefulness Evaluation** → The **LLM** checks if the content is relevant.
- **Context Extraction** → Extracts key information from relevant pages.

### 4. Iterative Refinement
- The **LLM** reviews gathered context and decides if additional searches are needed.
- If required, **new search queries** are generated; otherwise, the loop terminates.

### 5. Final Report Compilation
- All relevant information is compiled and passed to the **LLM**.
- The **LLM** generates a final **comprehensive research report**.
- The **report is printed** to the console and **saved as `final_report.txt`**.

---

## Troubleshooting

### PSReadline Warning
- If you see a **PSReadline** warning on Windows, you can safely ignore it.

### Asyncio Runtime Errors
- If you encounter: 
  ```
  RuntimeError: asyncio.run() cannot be called from a running event loop
  ```
  - Ensure **nest_asyncio** is applied at the start of the script:
    ```python
    import nest_asyncio
    nest_asyncio.apply()
    ```

### API Issues
- **Google API Errors:** Verify that your **Google API Key** and **Custom Search Engine ID** are correct.
- **Quota Limits:** Check if you've **exceeded** your Google API quota.

### Ollama Errors
- If the **local LLM** call fails:
  - Ensure **Ollama** is **installed correctly**.
  - Check that running:
    ```bash
    ollama run deepseek-r1:7b
    ```
    Works **without errors** in your terminal.

---

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

### 🔥 Contributions & Feedback
We welcome contributions! Feel free to fork, submit issues, or contribute to the project.

