"""
List the Gemini chat models available for the configured API key.

Reads GOOGLE_API_KEY from .env and prints every model that supports
text generation (generateContent), excluding embedding, image, audio,
TTS, live, robotics and preview/experimental variants.
"""

from pathlib import Path
import os
import sys

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Substrings identifying models that cannot serve as a chat model.
EXCLUDED_MARKERS = (
    "embedding",
    "image",
    "audio",
    "tts",
    "live",
    "robotics",
    "preview",
    "exp",
)


def is_chat_model(name: str, actions: list[str] | None) -> bool:
    """Return True for a stable Gemini text-generation model."""

    if not name.startswith("gemini-"):
        return False

    if actions and "generateContent" not in actions:
        return False

    return not any(marker in name for marker in EXCLUDED_MARKERS)


def main() -> None:
    """Print the available Gemini chat models."""

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not api_key or api_key.startswith("your_"):
        print(
            "GOOGLE_API_KEY is required.\n"
            "Create a free key at https://aistudio.google.com/apikey "
            "and set it in .env."
        )
        sys.exit(1)

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        listed = list(client.models.list())
    except Exception as error:
        # Keep only the leading summary of API errors, which append a
        # verbose JSON payload after the first brace.
        message = str(error).split(" {")[0].strip()
        print(f"Could not list models: {message}")
        sys.exit(1)

    models = []

    for entry in listed:
        name = (entry.name or "").removeprefix("models/")
        actions = getattr(entry, "supported_actions", None)

        if name and is_chat_model(name, actions):
            models.append(name)

    if not models:
        print("No chat models are available for this API key.")
        sys.exit(1)

    aliases = [name for name in models if name.endswith("-latest")]
    dated = [name for name in models if not name.endswith("-latest")]

    print("\nAvailable Gemini chat models:\n")

    for name in aliases + sorted(dated, reverse=True):
        print(f"✔ {name}")

    print()


if __name__ == "__main__":
    main()
