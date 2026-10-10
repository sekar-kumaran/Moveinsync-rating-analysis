import re

def clean_text(text: str) -> str:
    """
    Cleans a text string: lowercase, remove URLs, keep only a-z and whitespace, and strip.
    Must match the cleaning logic used during model training in the notebook.
    """
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()
