from llm.response_generator import generate_text

INTENT_PROMPT = """
You are an enterprise IT assistant.

Classify the user request into exactly ONE category:
- ACTION (creating a ticket, fixing an issue, requesting help)
- INFORMATION (asking a question)

User input:
"{query}"

Return ONLY the category name.
"""

def classify_intent(query: str) -> str:
    result = generate_text(INTENT_PROMPT.format(query=query), max_new_tokens=8).strip().upper()

    if result not in ("ACTION", "INFORMATION"):
        return "INFORMATION"

    return result
