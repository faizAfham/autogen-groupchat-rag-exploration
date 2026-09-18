"""LLM config for AutoGen agents. Swap providers by setting env vars, no code changes."""
import os


def get_config_list() -> list[dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env, fill in a key "
            "for any OpenAI-API-compatible provider, then `export $(cat .env | xargs)`."
        )
    entry = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "api_key": api_key,
    }
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        entry["base_url"] = base_url
    return [entry]
