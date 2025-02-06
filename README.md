# Local Deep Researcher

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

bash
pip install nest_asyncio aiohttp tenacity google-api-python-client newspaper3k

## Setup

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/local-deep-researcher.git
cd local-deep-researcher

### 2. Configure API Keys
- Open the main.py file.
- Replace the placeholders for GOOGLE_API_KEY and GOOGLE_CX with your actual Google API key and Custom Search Engine ID.
- If using Jina for webpage extraction, update JINA_API_KEY and JINA_BASE_URL as needed.

### 3. Ensure Ollama is Installed
Verify that Ollama is installed on your system and that running the following command works in your terminal:

```bash
pip install nest_asyncio aiohttp tenacity google-api-python-client newspaper3k

## Usage
### Run the Program
**Execute the main script from your terminal:**

```bash
python main.py

## Input Prompt
- **Research Query/Topic:**
When prompted, enter a research query or topic (e.g., "what is uap?").

-** Maximum Number of Iterations:**
Optionally, specify the maximum number of iterations (default is 10).

## Research Process
- **Initial Query & Search Generation:**
The local LLM (DeepSeek-R1:7b via Ollama) generates up to four distinct search queries based on your input.

- **Concurrent Search & Extraction:**
Each search query is sent concurrently to the Google Custom Search API. The program aggregates and deduplicates the returned links and fetches webpage content asynchronously.

- **Evaluation & Context Extraction:**
The local LLM evaluates each webpage for relevance and extracts pertinent context from useful pages.

- **Iterative Refinement:**
The aggregated context is analyzed by the LLM to decide if further search queries are required. The process repeats until the iteration limit is reached or no new queries are generated.

- **Final Report Generation & Saving:**
A detailed final report is compiled from all gathered context, printed to the console, and saved as final_report.txt in the project directory.



