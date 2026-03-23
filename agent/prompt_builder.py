def build_prompt(question: str, section_text: str, tables: list, page: str):

    prompt = f"""
Answer the question using ONLY the evidence below.

If the answer is not explicitly supported by the evidence, respond EXACTLY:
Information not found in the document.

Rules:
- Do not use outside knowledge.
- Do not guess or infer.
- Keep the answer concise and specific.
- Preserve numbers exactly as written in the evidence.
- Cite the page only when the evidence already shows a page label.

QUESTION:
{question}

TEXT EVIDENCE:
{section_text}
"""

    if tables:

        prompt += """

TABLE EVIDENCE:
"""

        for i, table in enumerate(tables, 1):

            prompt += f"""

Table {i}:
{table}
"""

    prompt += """

OUTPUT:
- If the answer is found, answer in 1-3 concise sentences.
- If a page is visible in the evidence, append `(Source: Page X)` using that page.
- Otherwise do not invent a page number.
"""

    return prompt.strip()
