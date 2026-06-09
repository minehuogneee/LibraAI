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


To strictly address the reproducibility requirements, this section provides exhaustive details of our data pipeline, model versions, API logic, and evaluation protocols.

### 1. Data Crawling & Collection
* A Python-based crawler connects to the E-commerce platform's API to periodically collect book metadata. 
* Scripts `get_categories.py` and `get_books.py` handle the data extraction with user-agent rotation and pagination. 
* The `automate_update_data.py` and `compare_data.py` scripts are used to detect data changes (deltas) and simulate real-time updates.
* **Crawl Date:** The primary book dataset used for the benchmark was collected on **April 1, 2025** (Refer to `books_data_2025-04-01_14-30-45.csv`).

### 2. Data Preprocessing & Graph Construction
* The collected records are normalized and compared with existing data. Only new or updated books are processed further to minimize computational overhead.
* **Text Chunking:** `process_tiki_books.py` structures the raw data into text chunks with exact token counts and metadata tracking.
* **Deterministic Knowledge Graph:** The `insert_custom_kg.py` script parses the raw CSV to construct deterministic KG entities (Authors, Prices, Categories) and relationships. This bypasses standard LLM-based extraction to ensure 100% data fidelity and prevent hallucination.

### 3. Model Versions & Dual-LLM Architecture
To optimize both retrieval routing and response generation, the system utilizes a specialized Dual-LLM architecture alongside a dedicated embedding model:
* **Embedding Model:** `nomic-embed-text` (Vector dimension explicitly configured to `768`).
* **Query Parsing & Routing Model:** `qwen2.5:7b`. Exclusively handles keyword extraction (`high_level_keywords` and `low_level_keywords`) to route queries efficiently.
* **Response Generation Model:** `gemma2:2b` via Ollama. Responsible for grounding the final answer within the retrieved context (Settings: `temperature=0.1`, `num_ctx=1024`).

### 4. API Endpoint Logic
The system is served via FastAPI (`lightrag_ollama_api.py`). To guarantee accurate benchmarking, the `/query` endpoint implements a **Two-step Retrieval Architecture** to strictly isolate context retrieval latency from LLM generation latency.

| Endpoint | Method | Execution Phase | Key Parameters / Flags | Purpose & Internal Logic |
| :--- | :---: | :--- | :--- | :--- |
| `/insert_custom_kg` | `POST` | **Ingestion** | `path`, `batch_size` | Ingests the deterministic custom Knowledge Graph batches into GraphDB and VectorDB, bypassing LLM extraction. |
| `/query` | `POST` | **Step 1: Context Measurement** | `mode="mix"`, `top_k=6`, `only_need_context=True` | Bypasses the generation LLM. Retrieves pure Graph + Vector context. Uses `tiktoken` (cl100k_base) to precisely measure `context_time` and `context_tokens`. |
| `/query` | `POST` | **Step 2: Response Generation** | `mode="mix"`, `top_k=6`, `only_need_context=False` | Triggers the full RAG pipeline. The generation model reads the context to output the final answer, capturing the `true_total_time` (Overall Latency). |

### 5. Prompt Templates
All core instructions are strictly defined in [`prompt.py`](https://github.com/minehuogneee/LibraAI/blob/main/lightrag/prompt.py), featuring robust control mechanisms:
* **Enrichment Rule:** Automatically injects related attribute keywords (Price, Rating, Author) if a specific book title is detected during the routing phase.
* **Rich Profile Rule:** The `---Thinking---` (Chain-of-Thought) framework forces the LLM to output a structured book profile prior to deep analysis.
* **Fallback Protocol:** The `no_context_response` template is activated strictly when the retrieved context vector similarity falls below the $\tau$ threshold to prevent hallucination.

### 6. Evaluation Protocols & Benchmark Settings
* **Evaluation Queries:** 125 curated questions were generated to cover diverse user intents (listing, comparing, factual queries). The prompt used to generate these questions is available at: [`user_question_prompt.txt`](https://github.com/minehuogneee/LibraAI/blob/main/user_question/user_question_prompt.txt).
* **Baseline Chatbot:** Actual production baseline responses were extracted using our `get_response_tiki_chatbot.py` script.
* **Execution Settings:** Evaluated using `mode="mix"` (Hybrid Graph + Vector Search) at `top_k = 6`.
* **LLM-as-a-Judge Pipeline:** Pairwise evaluation (LibraAI, LightRAG vs. MiniRAG) was conducted using the OpenAI Batch API (`Step_1_openai_batch_eval.py`) with **GPT-4o-mini** (configured at `temperature=0.2` for strict consistency). 
* **Evaluation Metrics:** The judge assesses outputs based on three specific criteria:
  * **Comprehensiveness:** How much detail does the answer provide to cover all aspects and details of the question?
  * **Diversity:** How varied and rich is the answer in providing different perspectives and insights on the question?
  * **Empowerment:** How well does the answer help the reader understand and make informed judgments about the topic?
     
---

## References
[1]	Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, and Chao Huang, ”LightRAG: Simple and Fast Retrieval-Augmented Generation”

