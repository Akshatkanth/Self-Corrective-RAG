# Self-Corrective RAG (CRAG)

An enterprise-grade, agentic Corrective Retrieval-Augmented Generation (CRAG) system built with **LangGraph**, **FAISS**, and **Groq (Llama-3.3)**.

Unlike standard RAG pipelines that blindly feed search results to an LLM, this system implements a self-correcting loop. It evaluates its own retrieved context, actively rewrites search queries if the results are irrelevant, and gracefully admits when information is missing, effectively eliminating hallucination.

## 🧠 Architecture Overview

The system operates as an intelligent state machine orchestrated by **LangGraph**:

1. **Retrieval**: Embeds the query using local `sentence-transformers` (`all-MiniLM-L6-v2`) and fetches the top 4 chunks from a local **FAISS** vector database.
2. **Grading (The "Bouncer")**: An LLM strictly evaluates the retrieved chunks against the original question.
3. **Routing**:
   - If the chunks are **relevant**, it routes to Answer Generation.
   - If the chunks are **irrelevant**, it routes to Query Rewriting (up to a max retry limit).
   - If retries are **exhausted**, it routes to a safe "Not Found" state.
4. **Query Rewriting**: The LLM analyzes the failure reasoning and formulates a new, vector-optimized search query.
5. **Answer Generation**: Generates the final answer using *only* the approved context, providing explicit source file citations.

## 📂 Project Structure

```
Self-Corrective-RAG/
├── docs/                      # Markdown files to be indexed
├── faiss_index/               # Generated FAISS vector database
├── corrective_rag/
│   ├── config.py              # Environment variables & warnings configuration
│   ├── ingest.py              # Document loading and chunking (RecursiveCharacterTextSplitter)
│   ├── vectorstore.py         # Embeddings (HuggingFace) and FAISS index management
│   ├── llm.py                 # Groq LLM connection and structured output plumbing
│   ├── grader.py              # Strict relevance evaluation
│   ├── rewrite.py             # Query reformulation logic
│   ├── generate.py            # Final answer generation with citations
│   └── graph.py               # LangGraph state machine orchestrator
├── main.py                    # Command Line Interface (CLI)
├── requirements.txt           # Project dependencies
└── .env.example               # Example environment variables
```

## 🚀 Setup & Installation

1. **Clone the repository and set up a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and add your Groq API key:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your `GROQ_API_KEY`.*

4. **Initialize the Vector Database**:
   *(Note: The CLI will automatically build this on its first run if it doesn't exist, but you can build it manually).*
   ```bash
   python corrective_rag/vectorstore.py
   ```

## 💻 Usage

Use the `main.py` CLI to ask questions about your documents.

**Standard Query (Clean Output)**
```bash
python main.py "how do I roll back a deployment"
```

**Verbose Query (Watch the Agent Think)**
Add the `--verbose` flag to see the exact execution trace as the agent retrieves, grades, and reformulates queries in real-time.
```bash
python main.py "how do we test if the system can handle a huge traffic spike" --verbose
```

## 🛠️ Technology Stack
- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **LLM / Inference**: [Groq](https://groq.com/) (Llama-3.3-70b-versatile)
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss) (faiss-cpu)
- **Embeddings**: [Sentence-Transformers](https://sbert.net/) (`all-MiniLM-L6-v2`)
- **Structured Output**: Pydantic
