import os

from dotenv import load_dotenv
from google import genai


# Load values from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Please add your Gemini API key to the .env file."
    )

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt: str) -> str:
    """
    Send a text prompt to Gemini and return the generated text.
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        raise RuntimeError("Gemini returned an empty response.")

    except Exception as exc:
        raise RuntimeError(
            f"Gemini API request failed: {exc}"
        ) from exc