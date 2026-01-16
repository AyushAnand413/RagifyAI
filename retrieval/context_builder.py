def build_context(filtered_chunks):
    """
    Build grounded context for the Agent.
    This is the ONLY information the LLM will see.
    """
    context = []

    for chunk in filtered_chunks:
        context.append({
            "section": chunk.get("section", ""),
            "pages": chunk.get("pages", []),
            # Defensive: never allow missing text
            "text": chunk.get("chunk_text", ""),
            "tables": chunk.get("tables", []),
            "images": chunk.get("images", [])
        })

    return {
        "context": context
    }
