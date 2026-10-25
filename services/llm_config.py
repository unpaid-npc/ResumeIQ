"""Build the language model connection from .env settings."""
import os

from crewai import LLM
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when .env settings are missing or still placeholders."""


def get_llm() -> LLM:
    load_dotenv(".env")
    provider = os.getenv("LLM_PROVIDER", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not provider or not model or not api_key or api_key.startswith("your_"):
        raise ConfigError("Set LLM_PROVIDER, LLM_MODEL and LLM_API_KEY in your .env file.")
    return LLM(model=f"{provider}/{model}", api_key=api_key, temperature=0.2)