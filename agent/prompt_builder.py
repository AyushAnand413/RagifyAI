def build_prompt(question, section_text, tables, page):
    """
    Constructs a strict, evidence-based prompt for the Financial Assistant.
    """
    prompt = f"""
You are an enterprise financial assistant.

TASK:
Extract the answer strictly from the evidence provided.
Do NOT calculate.
Do NOT explain formulas or reasoning.
If a percentage or value is explicitly stated, use it verbatim.
If the answer is NOT explicitly present in the evidence, respond exactly with:
"Information not found in the document."

QUESTION:
{question}

EVIDENCE:
"""

    # Only include page info as evidence, not as a mandate
    if page != "Unknown":
      prompt += f"\nPage Reference: {page}\n"


    prompt += f"""
TEXT:
{section_text}
"""

    if tables:
        prompt += "\nTABLE DATA (AUTHORITATIVE):\n"
        for i, table in enumerate(tables, 1):
            prompt += f"\nTable {i}:\n{table}\n"

    prompt += """
OUTPUT RULES (STRICT):
- If an answer IS FOUND:
  - Answer in 1–2 declarative sentences
  - Quote numbers exactly as shown
  - End the answer with: (Source: Page <page number>)
- If the answer IS NOT FOUND:
  - Respond with exactly: "Information not found in the document."
  - Do NOT include any page number
  - Do NOT add explanations
"""

    return prompt.strip()