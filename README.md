# LibraAI: A Lightweight Conversational AI System for Book Consultation in E-Commerce

LibraAI is an AI-powered chatbot that automatically crawls book information from **Tiki** on a scheduled basis and builds an intelligent knowledge base.  
Users can then query LibraAI in natural language to explore book details and receive suggestions to make better purchasing decisions.

---

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/minehuogneee/LibraAI.git
cd LibraAI/
```

### 2. Backend Setup (LightRAG + Ollama)
- Create a Python environment (Python 3.11 recommended) and install dependencies:
  ```bash
  conda create -n libraai python=3.11 -y
  conda activate libraai
  pip install -e .
  ```
- Install [Ollama](https://ollama.com) and pull required models:
  ```bash
  ollama pull nomic-embed-text
  ollama pull gemma2:2b
  ollama pull qwen2.5:7b
  ```
- Configure environment variables in a `.env` file (example included in repo).
- Start Ollama service:
  ```bash
  ollama serve
  ```
- Run backend API:
  ```bash
  python src/main/lightrag_ollama_api.py
  ```

### 3. Frontend Setup (Web UI)
The frontend is a lightweight static app located in `LibraAI_webui/`.  
Run it with any local server, for example:
```bash
cd LibraAI_webui
python3 -m http.server 3000
```
Then open: [http://localhost:3000](http://localhost:3000)

*(Make sure the backend API is running at `http://localhost:8000`.)*

### 4. Automated Updates
You can schedule automatic crawling and updating of book data with `cron`.  
Example (run daily at 18:51):
```bash
51 18 * * * cd /path/to/LibraAI && python ./src/main/automate_update_data.py >> ./logs/cron_log.txt 2>&1
```

---

## System Flow

The overall LibraAI workflow:

![LibraAI System Flowchart](docs/LibraAI_structure.svg)

1. **Data Crawling**  
   - A Python-based crawler connects to the Tiki API to periodically collect book metadata.  

2. **Data Preprocessing**  
   - The collected records are normalized and compared with existing data.  
   - Only new or updated books are processed further for knowledge base updates.  

3. **Knowledge Processing**  
   - Valid book data is embedded using an embedding model.  
   - Data is stored in LightRAG with entity–relation graphs for efficient retrieval.  

4. **Query & Response Generation**  
   - When a user sends a query, the system combines vector search with graph-based retrieval at two levels.  
   - A large language model generates natural language answers.
   
## Reproducibility & Benchmark Settings

To ensure full reproducibility of the experiments and benchmarks mentioned in our study, please refer to the following configurations and provided scripts:

### 1. Data Collection & Preprocessing
* **Crawl Date:** The primary book dataset used for the benchmark was collected from the E-commerce platform on **April 1, 2025** (Refer to `books_data_2025-04-01_14-30-45.csv`).
* **Crawling Logic:** Scripts `get_categories.py` and `get_books.py` handle the data extraction. The `automate_update_data.py` and `compare_data.py` scripts are used to detect data changes (deltas) and simulate real-time updates.
* **Preprocessing:** The `insert_custom_kg.py` script parses the raw CSV to construct deterministic Knowledge Graph entities (Authors, Prices, Categories) and relationships, bypassing standard LLM extraction to ensure 100% data fidelity.

### 2. Model Versions & API Endpoint Logic
The system is served via FastAPI (`lightrag_ollama_api.py`).
* **LLM Engine:** `gemma2:2b` via Ollama (Settings: `temperature=0.1`, `num_ctx=1024`).
* **Embedding Model:** `nomic-embed-text` (Vector dimension explicitly configured to `768`).
* **API Logic:** The `/query` endpoint implements a custom two-step retrieval architecture. It first extracts the context using `only_need_context=True` to accurately measure `context_time` and `context_tokens` (via `tiktoken`), followed by LLM generation to isolate retrieval latency from generation latency.

### 3. Prompt Templates & Evaluation Protocols
* **System Prompts:** All core instructions, including the `---Thinking---` framework (Chain-of-Thought) and `no_context_response` fallbacks, are strictly defined in `[prompt.py](https://github.com/minehuogneee/LibraAI/blob/main/lightrag/prompt.py)`.
* **Evaluation Queries:** 125 curated questions were generated to cover diverse user intents (listing, comparing, factual queries). The prompt used to generate these questions is available at: [user_question_prompt.txt](https://github.com/minehuogneee/LibraAI/blob/main/user_question/user_question_prompt.txt).
* **Benchmark Execution:** Evaluated at `top_k = 6`. Pairwise evaluation (LibraAI, LightRAG vs. MiniRAG) was conducted using the OpenAI Batch API (`Step_1_openai_batch_eval.py`) with GPT-4 as the judge, assessing Comprehensiveness, Diversity, and Empowerment.
- **Comprehensiveness**: How much detail does the answer provide to cover all aspects and details of the question?
- **Diversity**: How varied and rich is the answer in providing different perspectives and insights on the question?
- **Empowerment**: How well does the answer help the reader understand and make informed judgments about the topic?

     
---

## References
[1]	Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, and Chao Huang, ”LightRAG: Simple and Fast Retrieval-Augmented Generation”

