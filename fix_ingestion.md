# Ingestion Pipeline Fixes Proposal

This document outlines the root causes of the issues currently plaguing the data ingestion pipeline, how I plan to fix them, and what benefits the fixes will deliver. 

Please review this and tell me when you want me to apply the fixes.

## 1. Missing Content (Lists and Uncategorized Text)

### The Problem
The Unstructured document parser identifies bullet points as `ListItem` and plain text as `Text`. Currently, `c:\ML\RagifyAI\ingestion\router.py` explicitly throws away any element that is not a `Title` or `NarrativeText`. Furthermore, `c:\ML\RagifyAI\ingestion\chunker.py` is only configured to process `Title` and `NarrativeText`.

Because of this, all bulleted lists, numbered lists, and generic sub-texts are entirely dropped.

### The Fix
1. **Update `router.py`**: Add `ListItem` and `Text` to the allowed list so that they route into `text_elements.json` instead of `unknown_elements.json`.
2. **Update `chunker.py`**: Add a catch block `elif el_type in ["NarrativeText", "ListItem", "Text"]:` so that bullet points and plain text are appended to the `current_text` array. 
   - I will format `ListItem` elements by prepending a bullet character (e.g., `- `) so the model knows it was a list.

### Benefit
The RAG system will now have access to bulleted lists and formatting-heavy text that was previously invisible.

---

## 2. Giant Chunks and Silent Truncation

### The Problem
The embedding model (`BAAI/bge-base-en`) used in `c:\ML\RagifyAI\ingestion\runtime_ingestion.py` has a maximum context window of exactly **512 tokens** (roughly 350-400 words).
Currently, `chunker.py` merges all text elements falling under a single `Title` into one huge string. If a section of the PDF is 3 pages long, the combined chunk might be 2,000 words.
When `runtime_ingestion.py` embeds this 2,000-word block, the model silently truncates the last 1,600 words. They simply vanish from the vector store.

### The Fix
Instead of pushing out a single massive chunk per section, I will introduce a max-length splitting logic inside `chunker.py`.
1. Before calling `flush_chunk()`, I will check how many words/characters are in `current_text`.
2. If the text exceeds ~350 words, I will break it into multiple smaller, sub-chunks (e.g., `chunk_001_part1`, `chunk_001_part2`), ensuring no single chunk exceeds the embedding model context limit.
3. Each sub-chunk will retain the `Title` metadata and be embedded fully.

### Benefit
Documents with long narrative sections will be 100% ingested without silent truncation, dramatically improving semantic search recall on dense PDFs.

---

## 3. Extremely Naive Table Retrieval

### The Problem
In `table_processor.py`, the `generate_table_summary` function relies on basic hardcoded keyword matching like `if "revenue" in text_lower:`. If a table doesn't have the words "revenue", "profit", or "employee", it falls back to the generic summary: *"Unstructured table containing numeric or textual data."*
Because the index solely embeds the summary for semantic retrieval, any table that falls back to the generic string will share identical vector embeddings with every other generic table, making it almost impossible for the AI to retrieve them accurately based on user queries.

### The Fix
To properly index tables for retrieval, the summary must capture the actual table contents and context.
1. **Option A (AI Summarization - Recommended)**: If the backend has access to an LLM during ingestion (e.g., Llama-3.2-1B), I will replace `generate_table_summary` with a brief prompted LLM call that asks the model to look at the HTML/raw text and generate a 1-sentence descriptive summary of the table's purpose and contents.
2. **Option B (Content-based Heuristics)**: If an LLM is not desired during ingestion, I will extract all column headers and the first row of data, and programmatically inject them into the summary: e.g., *"Table containing columns: [Date, Region, Sales, Margin]."*

### Benefit
The semantic search will now have a highly specific, unique embedding for every single table, allowing the RAG system to accurately fetch the right table when asked a complex question.

---

*Let me know when you approve this plan and which Option (A or B) you prefer for the Table Processor!*
