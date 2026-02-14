---
title: Corporate Bot Backend
emoji: 🤖
sdk: docker
app_port: 7860
---
# Corporate-Bot ðŸ¤–

### Agentic Assistant for Annual Report Q&A and Workplace Actions

An **offline, agentic AI assistant** that can **accurately answer questions from large corporate PDFs** (HCLTech Annual Report) and **trigger structured workplace actions** (e.g., IT tickets, HR requests) â€” built for **real-time local demos**.

---

## ðŸš€ Problem Statement

Enterprises struggle to:

* Extract **accurate, page-cited answers** from long PDFs
* Avoid hallucinations in financial and compliance data
* Convert natural language commands into **structured actions**

**Corporate-Bot** solves this using a **production-grade RAG + Agent Supervisor architecture**, running fully **offline**.

---

## ðŸ§  Key Capabilities

### ðŸ“„ Chat with PDF (RAG)

* Ask factual or conceptual questions from the annual report
* Answers are **grounded**, **page-cited**, and **auditable**
* Handles **text, tables, and images** correctly

### âš™ï¸ Action Intelligence

* Understands intent (question vs action)
* Produces **structured JSON outputs** for actions
* Example:

  > â€œCreate a ticket for VPN not workingâ€

### ðŸ›‘ Hallucination Control

* Strict refusal logic for missing information
* No guessing on tables or financial data
* Explicit â€œInformation not foundâ€ responses

---

## ðŸ—ï¸ Architecture Overview

PDF
 â”‚
 â”œâ”€â–¶ Unstructured PDF Parser
 â”‚     â”œâ”€ Text
 â”‚     â”œâ”€ Tables (HTML preserved)
 â”‚     â””â”€ Images
 â”‚
 â”œâ”€â–¶ Structure-Aware Chunking
 â”‚
 â”œâ”€â–¶ Embeddings (BGE-base)
 â”‚
 â”œâ”€â–¶ FAISS Vector Index
 â”‚
 â”œâ”€â–¶ Retriever (Top-K Recall)
 â”‚
 â”œâ”€â–¶ Cross-Encoder Reranker
 â”‚
 â”œâ”€â–¶ Context Builder
 â”‚
 â”œâ”€â–¶ Agent Supervisor
 â”‚     â”œâ”€ Intent Classification
 â”‚     â”œâ”€ Refusal Logic
 â”‚     â”œâ”€ Action Routing
 â”‚
 â””â”€â–¶ LLM (Ollama â€“ Mistral 7B)


---

## ðŸ” RAG Design (Important)

### âœ” Structure-Preserving Tables

* Tables are **never flattened**
* HTML is preserved at extraction time
* Numeric answers always come from source tables

### âœ” Two-Stage Retrieval

1. **Bi-encoder retrieval** (wide recall)
2. **Cross-encoder reranking** (high precision)

### âœ” Evidence-Only Context

The LLM only sees:

* Retrieved text
* Table references
* Page numbers
  â†’ **No hallucinations**

---

## ðŸ§‘â€ðŸ’» Tech Stack

| Component   | Tool                  |
| ----------- | --------------------- |
| PDF Parsing | unstructured        |
| Embeddings  | BAAI/bge-base-en    |
| Vector DB   | FAISS                 |
| Reranker    | ms-marco-MiniLM     |
| LLM         | Ollama (mistral:7b) |
| Backend     | Flask                 |
| Frontend    | HTML + CSS + JS       |
| Language    | Python                |

---

## ðŸ“ Project Structure

Corporate-bot/
â”‚
â”œâ”€â”€ actions/              # Action registry & execution
â”œâ”€â”€ agent/                # Agent supervisor & intent logic
â”œâ”€â”€ ingestion/            # PDF parsing, tables, chunking
â”œâ”€â”€ retrieval/            # Embedding, FAISS, reranking
â”œâ”€â”€ llm/                  # Ollama client & response generator
â”œâ”€â”€ templates/            # HTML frontend
â”œâ”€â”€ static/               # CSS & JS
â”œâ”€â”€ evaluation/           # Retrieval tests & debug tools
â”œâ”€â”€ utils/                # Helpers & logging
â”‚
â”œâ”€â”€ app.py                # Core pipeline entry
â”œâ”€â”€ web_app.py            # Flask web server
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md


---

## â–¶ï¸ How to Run Locally (Offline)

### 1ï¸âƒ£ Prerequisites

* Python 3.9+
* Ollama installed
* Model pulled:

bash
ollama pull mistral


---

### 2ï¸âƒ£ Install Dependencies

bash
pip install -r requirements.txt


---

### 3ï¸âƒ£ Start the Application

bash
python web_app.py


Open in browser:

http://localhost:5000


---

## ðŸ§ª Example Queries

### ðŸ“„ PDF Question

**Q:** What was the revenue growth in FY25?
**A:**

> Revenue growth in FY25 was **6.5%**.
> *(Source: Page 107)*

---

### ðŸ§  Conceptual Question

**Q:** What are the key risks mentioned by the company?
**A:**

> Summarized explanation with page citations

---

### âš™ï¸ Action Command

**Q:** Create a ticket for VPN not working
**Output JSON:**

json
{
  "action": "create_ticket",
  "department": "IT",
  "priority": "High",
  "description": "VPN not working"
}


---

### ðŸ›‘ Refusal Case

**Q:** What is the quantum entanglement revenue?
**A:**

> Information not found in the document.

---

## ðŸ§¾ Evaluation Criteria Alignment

| Criteria               | How We Address It                     |
| ---------------------- | ------------------------------------- |
| Accuracy (30%)         | Page-cited RAG, table-safe extraction |
| Agent Capability (30%) | Deterministic action JSON             |
| Impact (25%)           | Digital workplace automation          |
| Presentation (15%)     | Clean UI + explainable architecture   |

---

## ðŸ” Safety & Trust

* No hallucinated numbers
* No table reconstruction from text
* Explicit refusals when evidence is missing
* Fully auditable answers

---

## ðŸ Conclusion

**Corporate-Bot** demonstrates a **real-world, production-ready agentic assistant** that combines:

* Accurate document intelligence
* Robust retrieval
* Deterministic action execution

Designed specifically for **enterprise-grade trust and offline demos**.

---

