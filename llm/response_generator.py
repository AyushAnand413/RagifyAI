import os

from llm.hf_inference_client import HFGenerationError, HFInferenceClient


_intent_client = HFInferenceClient(
    api_token=os.getenv("HF_TOKEN", ""),
    generation_model=os.getenv("HF_INTENT_MODEL", os.getenv("HF_GENERATION_MODEL", "meta-llama/Llama-3.2-3B-Instruct:novita")),
    timeout=int(os.getenv("HF_INTENT_TIMEOUT", "45")),
)


def generate_text(prompt: str, max_new_tokens: int = 32) -> str:
    """
    HF-only generation path for lightweight tasks like intent classification.
    Returns empty string on inference failure so callers can apply safe defaults.
    """
    try:
        return _intent_client.generate(prompt, max_new_tokens=max_new_tokens)
    except HFGenerationError as e:
        print(f"HF intent generation failed: {e}")
        return ""
