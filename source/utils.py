import re


def slugify(s: str) -> str:
    return s.lower().replace(" ", "-").replace("'", "").replace("\"", "")

def strip_non_ascii(s: str):
    stripped = (c for c in s if 0 < ord(c) < 127)
    return ''.join(stripped)

def strip_non_basic_characters(s: str):
    return re.sub(r'[^a-zA-Z0-9_\-]', '', s)
