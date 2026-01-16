# agent/preprocess.py

import re

def normalize_query(query: str) -> str:
    """
    Lightweight normalization before planner/RAG.

    - Lowercases
    - Removes excess whitespace
    - Keeps original semantics intact
    """

    if not isinstance(query, str):
        return ""

    # Lowercase
    q = query.lower()

    # Collapse multiple spaces
    q = re.sub(r"\s+", " ", q)

    # Trim
    q = q.strip()

    return q
