
# 🤖 Corporate-Bot — Enterprise RAG Assistant

**Corporate-Bot** is a production-grade, agentic Retrieval-Augmented Generation (RAG) assistant that enables users to upload corporate PDFs and interact with them using natural language.

It provides **accurate, grounded answers and structured workplace actions** powered by HuggingFace-hosted LLM inference.

---

# 🌐 Live Architecture

Frontend: Next.js (Vercel)
Backend: Flask API (HuggingFace Spaces — Docker)
LLM: HuggingFace Inference API (meta-llama/Llama-3.2-3B-Instruct:novita)

---

# 🚀 Core Capabilities

## 📄 Document Intelligence (RAG)

Upload any corporate PDF and:

* Ask factual questions
* Get grounded answers
* Receive structured responses
* Prevent hallucinations

Supports:

* Text
* Tables
* Structured content

---

## ⚙️ Agent-Based Reasoning

The system intelligently detects user intent:

Example:

**User Input**

> Create a ticket for VPN not working

**Output**

```json
{
  "action": "create_ticket",
  "department": "IT",
  "priority": "High",
  "description": "VPN not working"
}
```

---

## 🛡️ Hallucination Control

Strict refusal logic:

If answer not present:

> Information not found in uploaded document.

No guessing. No fabricated answers.

---

# 🧠 Architecture Overview

```
PDF Upload
   ↓
Unstructured Parser
   ↓
Structure-Aware Chunking
   ↓
Embedding (BGE)
   ↓
FAISS Vector Store
   ↓
Retriever
   ↓
Cross-Encoder Reranker
   ↓
Agent Supervisor
   ↓
HuggingFace LLM Inference
   ↓
Final Response
```

---

# 🧰 Technology Stack

| Component        | Tool                   |
| ---------------- | ---------------------- |
| Backend          | Flask                  |
| Frontend         | Next.js                |
| Embeddings       | BAAI/bge-small-en      |
| Vector DB        | FAISS                  |
| Reranker         | cross-encoder/ms-marco |
| LLM              | HuggingFace Inference  |
| PDF Parser       | Unstructured           |
| Hosting          | HuggingFace Spaces     |
| Frontend Hosting | Vercel                 |

---

# 🌐 Live API Endpoints

## Health Check

```
GET /
```

Response:

```json
{
 "success": true
}
```

---

## Upload PDF

```
POST /api/v1/upload
```

---

## Ask Question

```
POST /api/v1/chat
```

---

# 🌍 Live Deployment

Backend:

```
https://AyushAnand413-corporate-rag-bot-backend.hf.space
```

Frontend:

```
(Your Vercel URL)
```

---

# 🧪 Example Queries

## Factual

> What is the vision of 6G networks?

---

## Table-based

> What was revenue growth in FY25?

---

## Conceptual

> What are key risks mentioned?

---

## Action

> Create a ticket for VPN not working

---

# 🔐 Security & Safety

✔ No hallucinated data
✔ Evidence-based answers
✔ Strict refusal logic
✔ Secure inference via HF Token

---

# 🧑‍💻 Local Development

## Requirements

Python 3.10+

---

## Install

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python web_app.py
```

Open:

```
http://localhost:7860
```

---

# 🔑 Environment Variables

Required:

```
HF_TOKEN=your_token
```

Optional:

```
HF_GENERATION_MODEL=meta-llama/Llama-3.2-3B-Instruct:novita
ALLOWED_ORIGINS=*
```

---

# 📁 Project Structure

```
Corporate-bot/
│
├ agent/
├ ingestion/
├ retrieval/
├ llm/
├ frontend/
├ web_app.py
├ Dockerfile
└ requirements.txt
```

---

# 📈 Production Features

✔ Docker deployment
✔ CI/CD via GitHub Actions
✔ HF Spaces hosting
✔ Vercel frontend
✔ Runtime PDF ingestion
✔ API-first backend

---

# 🎯 Use Cases

Enterprise assistants
Corporate document search
Legal document QA
Financial report analysis
Internal automation bots

---

# 🧠 Model Used

```
meta-llama/Llama-3.2-3B-Instruct:novita
```

Hosted via:

HuggingFace Inference API

---

# 👨‍💻 Author

Ayush Kumar Anand

Swarnim Vatsyayan

Shuchay Viswanathan

---

# ⭐ Conclusion

Corporate-Bot is a fully production-ready enterprise AI assistant combining:

* Retrieval-Augmented Generation
* Agent-based reasoning
* Secure cloud inference
* Modern frontend architecture

---
