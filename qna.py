import os
import time

from dotenv import load_dotenv

load_dotenv()


def _extract_generated_text(response) -> str | None:
    if response is None:
        return None

    if isinstance(response, str):
        return response.strip() or None

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", None)
    if candidates:
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None)
            if parts:
                for part in parts:
                    part_text = getattr(part, "text", None)
                    if isinstance(part_text, str) and part_text.strip():
                        return part_text.strip()

    if isinstance(response, dict):
        for key in ("text", "output_text", "content"):
            value = response.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for candidate in response.get("candidates", []):
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content", {})
            for part in content.get("parts", []):
                if not isinstance(part, dict):
                    continue
                text_value = part.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    return text_value.strip()

    return None


def _is_retryable_gemini_error(exc: Exception) -> bool:
    if exc is None:
        return False

    message = str(exc).upper()
    return "503" in message or "UNAVAILABLE" in message


def answer_question(question: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    if not api_key or not api_key.strip():
        raise ValueError("Missing GEMINI_API_KEY in .env. Add your Google API key before using Ask Genie.")

    last_error = None

    for attempt in range(3):
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=question,
            )

            extracted = _extract_generated_text(response)
            if extracted:
                return extracted

            raise ValueError("Gemini returned an empty response for the submitted question.")

        except Exception as exc:
            last_error = exc
            if not _is_retryable_gemini_error(exc):
                raise RuntimeError(f"Gemini API request failed: {exc}") from exc

            if attempt < 2:
                delay = 2 ** attempt * 2
                time.sleep(delay)
                continue

    raise RuntimeError(
        "Gemini is temporarily unavailable right now. Please try again in a moment. "
        f"Last error: {last_error}"
    ) from last_error
