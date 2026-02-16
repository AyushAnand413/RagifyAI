import os
from typing import Any

import requests


class HFGenerationError(Exception):
    pass


class HFInferenceClient:
    def __init__(self, api_token: str, generation_model: str, timeout: int = 90):
        self.api_token = api_token or os.getenv("HF_TOKEN", "")
        self.generation_model = generation_model
        self.timeout = timeout
        self.url = os.getenv("HF_INFERENCE_V1_URL", "https://router.huggingface.co/v1/chat/completions")

    def _extract_text(self, payload: Any) -> str:
        if isinstance(payload, dict) and "choices" in payload:
            choices = payload.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    message = first.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
                        if isinstance(content, str):
                            text = content.strip()
                            if text:
                                return text

        if isinstance(payload, dict):
            if "error" in payload:
                raise HFGenerationError(str(payload.get("error", "HF inference error")))

            if "generated_text" in payload and isinstance(payload["generated_text"], str):
                text = payload["generated_text"].strip()
                if text:
                    return text

            if "summary_text" in payload and isinstance(payload["summary_text"], str):
                text = payload["summary_text"].strip()
                if text:
                    return text

        if isinstance(payload, list) and payload:
            first = payload[0]
            if isinstance(first, dict):
                if "error" in first:
                    raise HFGenerationError(str(first.get("error", "HF inference error")))

                generated_text = first.get("generated_text")
                if isinstance(generated_text, str):
                    text = generated_text.strip()
                    if text:
                        return text

                summary_text = first.get("summary_text")
                if isinstance(summary_text, str):
                    text = summary_text.strip()
                    if text:
                        return text

        raise HFGenerationError("Invalid HF response format")

    def generate(self, prompt: str, max_new_tokens: int = 256) -> str:
        if not self.api_token:
            raise HFGenerationError("HF token missing. Set HF_TOKEN environment variable.")

        headers = {}
        headers["Authorization"] = f"Bearer {self.api_token}"

        payload = {
            "model": self.generation_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_new_tokens,
            "temperature": 0.1,
            "top_p": 0.9,
        }

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.Timeout as e:
            raise HFGenerationError("HF inference timeout") from e
        except requests.RequestException as e:
            raise HFGenerationError(f"HF inference request failed: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise HFGenerationError("Invalid HF response format") from e

        text = self._extract_text(data)
        if not text:
            raise HFGenerationError("Invalid HF response format")

        return text
