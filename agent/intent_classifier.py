def classify_intent(query: str) -> str:
    query_lower = query.lower()

    action_keywords = [
        "create", "raise", "schedule",
        "book", "open ticket", "file ticket"
    ]

    for kw in action_keywords:
        if kw in query_lower:
            return "ACTION"

    return "INFORMATION"
