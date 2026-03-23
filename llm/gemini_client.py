import os

from google import genai
from google.genai import types


class GeminiGenerationError(Exception):
    """Custom exception for Gemini generation errors."""


class GeminiClient:

    def __init__(
        self,
        api_key: str = None,
        generation_model: str = None,
        timeout: int = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.generation_model = (
            generation_model
            or os.getenv("GEMINI_MODEL")
            or "gemini-2.5-flash"
        )
        self.timeout = int(timeout or os.getenv("GEMINI_TIMEOUT", "120"))
        self.disable_thinking = os.getenv("GEMINI_DISABLE_THINKING", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }
        self.client = None

        print("Gemini Model:", self.generation_model)

    def _client(self):
        if not self.api_key:
            raise GeminiGenerationError("GEMINI_API_KEY missing in environment")

        if self.client is None:
            self.client = genai.Client(api_key=self.api_key)

        return self.client

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ) -> str:
        try:
            config_kwargs = {
                "temperature": temperature,
                "top_p": top_p,
                "max_output_tokens": max_new_tokens,
            }

            if self.disable_thinking and self.generation_model.startswith("gemini-2.5"):
                config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

            response = self._client().models.generate_content(
                model=self.generation_model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )

            text = (getattr(response, "text", "") or "").strip()

            if not text:
                raise GeminiGenerationError("Gemini returned an empty response")

            return text

        except GeminiGenerationError:
            raise
        except Exception as exc:
            raise GeminiGenerationError(str(exc)) from exc
