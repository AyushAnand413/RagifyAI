import os

from llm.gemini_client import GeminiClient, GeminiGenerationError
from llm.hf_inference_client import HFGenerationError, HFInferenceClient


def create_generation_client(task: str = "generation"):
    backend = os.getenv("LLM_BACKEND", "hf").strip().lower()

    if task == "intent":
        backend = os.getenv("LLM_INTENT_BACKEND", backend).strip().lower()

    if backend == "gemini":
        if task == "intent":
            client = GeminiClient(
                api_key=os.getenv("GEMINI_API_KEY", ""),
                generation_model=os.getenv(
                    "GEMINI_INTENT_MODEL",
                    os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                ),
                timeout=int(os.getenv("GEMINI_INTENT_TIMEOUT", os.getenv("GEMINI_TIMEOUT", "45"))),
            )
        else:
            client = GeminiClient(
                api_key=os.getenv("GEMINI_API_KEY", ""),
                generation_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                timeout=int(os.getenv("GEMINI_TIMEOUT", "120")),
            )
        return client, GeminiGenerationError

    if task == "intent":
        client = HFInferenceClient(
            api_token=os.getenv("HF_TOKEN", ""),
            generation_model=os.getenv(
                "HF_INTENT_MODEL",
                os.getenv("HF_GENERATION_MODEL", "meta-llama/Llama-3.2-3B-Instruct:novita"),
            ),
            timeout=int(os.getenv("HF_INTENT_TIMEOUT", "45")),
        )
    else:
        client = HFInferenceClient(
            api_token=os.getenv("HF_TOKEN", ""),
            generation_model=os.getenv(
                "HF_GENERATION_MODEL",
                "meta-llama/Llama-3.2-3B-Instruct:novita",
            ),
            timeout=120,
        )

    return client, HFGenerationError
