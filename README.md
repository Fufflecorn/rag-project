# RAG Learning App

A Retrieval-Augmented Generation (RAG) application built with Python, ChromaDB, SentenceTransformers, and Google Gemini. You'll build this incrementally over Weeks 10–15.

## What This App Does

You can ask this app questions about Python, machine learning, databases, APIs, and AI concepts. It finds the most relevant documents from its knowledge base and sends them to Gemini as context — so the answers are grounded in real information rather than guesswork.

## System Architecture

```
User Query
    │
    ▼
[security.py]      ← Validate and sanitize input (Week 12)
    │
    ▼
[workflow.py]      ← Rewrite query for better retrieval (Week 15)
    │
    ▼
[embeddings.py]    ← Convert query to a vector
    │
    ▼
[vector_store.py]  ← Find similar document vectors in ChromaDB
    │
    ▼
[filters.py]       ← Remove irrelevant results (Week 14)
    │
    ▼
[rag_pipeline.py]  ← Build prompt with retrieved context
    │
    ▼
  Gemini API       ← Generate answer
    │
    ▼
[monitoring.py]    ← Check for hallucinations (Week 13)
    │
    ▼
[app.py]           ← Display answer, sources, confidence
```

## Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd student-rag-project
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your Gemini API key

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and replace `your-gemini-api-key-here` with your actual key.
Get a free key at: https://aistudio.google.com/apikey

### 5. Run the app
```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web interface |
| `config.py` | Configuration constants |
| `embeddings.py` | Convert text to vector embeddings |
| `vector_store.py` | Store and search vectors with ChromaDB |
| `data_loader.py` | Sample tech documents |
| `rag_pipeline.py` | Central orchestration — ties everything together |
| `conversation.py` | Conversation history (Week 11) |
| `security.py` | Input validation and security (Week 12) |
| `monitoring.py` | Hallucination detection (Week 13) |
| `filters.py` | Similarity filtering and fallbacks (Week 14) |
| `workflow.py` | Query rewriting and multi-hop retrieval (Week 15) |

---

## Weekly Progress

Update this checklist as you complete each week's assignment.

- [x] Week 10 — Ran the starter app and explored the codebase
- [x] Week 11 — Implemented conversation context
- [x] Week 12 — Implemented input security
- [x] Week 13 — Implemented hallucination monitoring
- [x] Week 14 — Implemented filtering and fallbacks
- [x] Week 15 — Implemented multi-step AI workflows

## 🔒 Compliance & Data Protection (SOC 2 Principles)

### Applicable Trust Principles
- **Privacy:** Responsible handling and automated masking of Personally Identifiable Information (PII).
- **Confidentiality:** Preventing exposure of credentials, API keys, and internal documents across public logs.
- **Security:** Enforcing strict boundary sanitization before data touches downstream LLM providers.

### Metadata Tagging Scheme
| Tag Key | Possible Values | Description |
| :--- | :--- | :--- |
| `sensitivity` | `public`, `internal`, `confidential`, `restricted` | Data access classification level |
| `data_type` | `operational`, `PII`, `credential` | High-level data category |
| `source` | `user_input`, `document`, `model_output` | Origin point in the RAG pipeline |

### Redaction Boundaries
Automated regex pattern matching (`security.py`) masks email addresses, telephone numbers, Social Security Numbers, and API keys (`[REDACTED_TYPE]`) prior to:
1. Forwarding text to Gemini or vector embeddings.
2. Persisting chat exchanges to session history.
3. Writing debug output to application logs.