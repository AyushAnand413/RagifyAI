from llm.client_factory import create_generation_client


_intent_client, _intent_error = create_generation_client(task="intent")


def generate_text(prompt: str, max_new_tokens: int = 32) -> str:
    """
    Backend-agnostic generation path for lightweight tasks like intent classification.
    Returns empty string on inference failure so callers can apply safe defaults.
    """
    try:
        return _intent_client.generate(prompt, max_new_tokens=max_new_tokens)
    except _intent_error as e:
        print(f"Intent generation failed: {e}")
        return ""
