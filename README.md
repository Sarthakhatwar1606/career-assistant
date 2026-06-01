# Career Assistant

A fully local AI career coach built with **Llama 3.1**, **nomic-embed-text**, and **Streamlit**.  
Your resume never leaves your machine — everything runs via Ollama.

## Features
- Upload your resume (PDF or plain text)
- Ask anything: improve your resume, write cover letters, find skill gaps, get job title suggestions
- Streaming responses with full chat history
- RAG (Retrieval-Augmented Generation) — answers are grounded in *your* resume

## Quick Start

```bash
# 1. Pull models (one-time)
ollama pull llama3.1
ollama pull nomic-embed-text

# 2. Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

## Models Used
| Model | Purpose |
|-------|---------|
| `llama3.1` | Chat / generation |
| `nomic-embed-text` | Resume embeddings for RAG |

## Stack
- **Streamlit** — UI
- **Ollama** — local LLM inference
- **ChromaDB** — in-memory vector store
- **pypdf** — PDF parsing
