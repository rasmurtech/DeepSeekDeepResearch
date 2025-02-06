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
 
Setup
Clone or Download the Repository:

bash
Copy
git clone https://github.com/yourusername/local-deep-researcher.git
cd local-deep-researcher
Configure API Keys:

Open the main.py file.
Replace the placeholders for GOOGLE_API_KEY and GOOGLE_CX with your actual API key and custom search engine ID.
If using Jina for webpage extraction, replace the JINA_API_KEY and update JINA_BASE_URL as needed.
Ensure Ollama is Installed:

Verify that Ollama is installed on your system and that the command below works in your terminal:

bash
Copy
ollama run deepseek-r1:7b
Usage
Run the Program:

Execute the Python file from your terminal:

bash
Copy
python main.py
Input Prompt:

The program will prompt you to enter:

A research query/topic (e.g., "what is uap?")
An optional maximum number of iterations (default is 10)
Follow the Research Process:

Initial Query & Search Generation:
The local LLM (DeepSeek-R1:7b via Ollama) generates up to four search queries based on your input.

Concurrent Search & Extraction:
For each search query, the program performs Google searches concurrently, aggregates unique links, and fetches webpage content asynchronously.

Evaluation & Context Extraction:
Each unique link is evaluated for usefulness by the local LLM. If deemed useful, relevant context is extracted.

Iterative Refinement:
The aggregated context is analyzed by the LLM to decide if further search queries are required. The process repeats for the specified number of iterations or until no additional queries are needed.

Final Report Generation:
Once the research loop is complete, the final report is generated and printed to the console.

Report Saving:
The final detailed report is also saved in the file final_report.txt in the repository directory.

How It Works
Input & Query Generation:
The user enters a research query, and the local LLM generates a JSON array of up to four distinct search queries.

Concurrent Google Searches:
Each generated search query is sent to the Google Custom Search API concurrently. The links returned are aggregated and deduplicated.

Webpage Processing:
Each unique link is processed asynchronously:

Content Extraction:
The webpage content is extracted using Newspaper3k (or Jina as a fallback).
Usefulness Evaluation:
The local LLM evaluates if the extracted content is relevant.
Context Extraction:
If useful, relevant context is extracted from the content.
Iterative Refinement:
After processing the links, the aggregated context is analyzed by the LLM to determine if more search queries are needed. If yes, new queries are generated and the loop repeats.

Final Report Compilation:
All gathered context is compiled and sent to the local LLM to generate a detailed final report addressing the original query.

Output:
The report is printed on the console and saved as final_report.txt in the project directory.

Troubleshooting
PSReadline Warning:
You might see a message about the PSReadline module when running the script on Windows. This is not an error and can be ignored.

Asyncio RuntimeError:
If you encounter an error like RuntimeError: asyncio.run() cannot be called from a running event loop, ensure that nest_asyncio is properly applied (as shown in the first lines of the script).

API Issues:
Ensure that your Google API keys are correct and that you have not exceeded your usage quota.

Ollama Errors:
If the local LLM call fails, verify that Ollama is installed correctly and that the command ollama run deepseek-r1:7b functions from your terminal.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Install the Python dependencies using pip:

```bash
pip install nest_asyncio aiohttp tenacity google-api-python-client newspaper3k
