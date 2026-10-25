"""Sends one tiny message to the model to prove the connection works."""
import os

from services.llm_config import ConfigError, get_llm


def main() -> None:
    try:
        llm = get_llm()
        reply = llm.call("Reply with exactly these words: ResumeIQ connection works")
        print("Model replied:", reply)
    except ConfigError as exc:
        print("Config problem:", exc)
    except Exception as exc:
        message = str(exc).replace(os.getenv("LLM_API_KEY", "@@none@@"), "***")
        print(f"Call failed ({type(exc).__name__}): {message[:600]}")


if __name__ == "__main__":
    main()