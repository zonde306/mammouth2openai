import os

MODELS = [
    "anthropic-claude-3-7-sonnet-latest",
    "openai-gpt-4.1",
    "openai-gpt-4.1-search-preview",
]

PROXIES = os.environ.get("PROXIES", None)
COOKIES : list[str] = [ x.strip() for x in os.environ.get("COOKIES", "").split(",") if x.strip() ]
PASSWORD : str = os.environ.get("PASSWORD", "")
INPUT_CHARS_LIMIT : int = int(os.environ.get("INPUT_CHARS_LIMIT", 1000000))
