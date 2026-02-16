# ============================================================
# PURE RAG PROMPT BUILDER (PRODUCTION GRADE)
# Optimized for small models like Llama-3.2-1B
# ============================================================


def build_prompt(question: str, section_text: str, tables: list, page: str):

    prompt = f"""
You are a strict enterprise document question-answering assistant.

You MUST follow these rules EXACTLY.


==============================
PRIMARY RULE
==============================

Answer ONLY using the information provided in EVIDENCE below.

DO NOT use outside knowledge.

DO NOT guess.

DO NOT infer.

DO NOT assume.

DO NOT add extra information.


==============================
IF ANSWER NOT FOUND
==============================

If the answer is not explicitly present in the evidence, respond EXACTLY:

Information not found in the document.


==============================
QUESTION
==============================

{question}


==============================
EVIDENCE
==============================

TEXT EVIDENCE:

{section_text}

"""


    # -------------------------------------------------------
    # ADD TABLES (VERY IMPORTANT)
    # -------------------------------------------------------

    if tables:

        prompt += """

TABLE EVIDENCE:
"""

        for i, table in enumerate(tables, 1):

            prompt += f"""

Table {i}:
{table}

"""


    # -------------------------------------------------------
    # OUTPUT FORMAT (STRICT)
    # -------------------------------------------------------

    prompt += """

==============================
OUTPUT FORMAT
==============================

If answer is found:

• Answer in correct and concise sentences.

• Use EXACT words from evidence.

• DO NOT rephrase numbers.

• DO NOT explain extra.

• ALWAYS end answer with source page like:

(Source: Page X)


==============================
IMPORTANT
==============================

Never answer without evidence.

Never fabricate page numbers.

Never answer from outside knowledge.

"""


    return prompt.strip()
