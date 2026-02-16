import os
import time
from typing import Any

import requests

# Safe dotenv loading (won't crash in CI)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class HFGenerationError(Exception):
    """Custom exception for HuggingFace generation errors."""
    pass


class HFInferenceClient:

    def __init__(
        self,
        api_token: str = None,
        generation_model: str = None,
        timeout: int = None,
        max_retries: int = None,
    ):
        """
        Initialize HF client safely.
        DO NOT crash if HF_TOKEN missing.
        """

        # Load token but DO NOT validate here
        self.api_token = api_token or os.getenv("HF_TOKEN")

        # Model fallback chain
        self.generation_model = (
            generation_model
            or os.getenv("HF_GENERATION_MODEL")
            or "meta-llama/Llama-3.2-1B-Instruct:novita"
        )

        # Timeout and retry config
        self.timeout = int(
            timeout or os.getenv("HF_TIMEOUT", "120")
        )

        self.max_retries = int(
            max_retries or os.getenv("HF_MAX_RETRIES", "5")
        )

        # HF router endpoint
        self.url = os.getenv(
            "HF_INFERENCE_V1_URL",
            "https://router.huggingface.co/v1/chat/completions"
        )

        print("HF Model:", self.generation_model)

    # ------------------------------------------------
    # Extract response text safely
    # ------------------------------------------------

    def _extract_text(self, payload: Any) -> str:

        try:

            return payload["choices"][0]["message"]["content"].strip()

        except Exception:

            if isinstance(payload, dict) and "error" in payload:

                raise HFGenerationError(
                    payload["error"]
                )

            raise HFGenerationError(
                f"Invalid HF response format: {payload}"
            )

    # ------------------------------------------------
    # Generate text
    # ------------------------------------------------

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.1,
        top_p: float = 0.9
    ) -> str:

        # ✅ Validate token HERE (not in __init__)
        if not self.api_token:

            raise HFGenerationError(
                "HF_TOKEN missing in environment"
            )

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.generation_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        for attempt in range(self.max_retries):

            try:

                print(f"HF attempt {attempt+1}")

                response = requests.post(
                    self.url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )

                # Rate limit handling
                if response.status_code == 429:

                    wait = 10 * (attempt + 1)

                    print(f"Rate limit. Waiting {wait}s")

                    time.sleep(wait)

                    continue

                response.raise_for_status()

                return self._extract_text(
                    response.json()
                )

            except requests.Timeout:

                print("Timeout retrying...")

            except requests.RequestException as e:

                print("Request failed:", e)

            time.sleep(3)

        raise HFGenerationError(
            "HF inference failed after retries"
        )


# ------------------------------------------------
# Test
# ------------------------------------------------

if __name__ == "__main__":

    client = HFInferenceClient()

    try:

        result = client.generate(
            "Explain AI simply"
        )

        print("\nResponse:\n")
        print(result)

    except HFGenerationError as e:

        print("\nError:\n", e)
