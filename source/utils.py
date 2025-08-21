import re


def slugify(s: str) -> str:
    """
    Convert a string into a simple "slug" form for URLs or identifiers.

    Operations performed:
        - Lowercase the string.
        - Replace spaces with dashes ("-").
        - Remove single quotes (') and double quotes (").

    Args:
        s (str): Input string.

    Returns:
        str: A slugified version of the input string.
    """
    return s.lower().replace(" ", "-").replace("'", "").replace("\"", "")

def strip_non_ascii(s: str):
    """
    Remove all non-ASCII characters from a string.

    Args:
        s (str): Input string.

    Returns:
        str: String containing only ASCII characters (ordinal 1–126).
    """
    stripped = (c for c in s if 0 < ord(c) < 127)
    return ''.join(stripped)

def strip_non_basic_characters(s: str):
    """
    Remove all characters except alphanumerics, underscores, and dashes.

    Allowed characters:
        - a–z
        - A–Z
        - 0–9
        - "_" (underscore)
        - "-" (dash)

    Args:
        s (str): Input string.

    Returns:
        str: Cleaned string with only the allowed characters.
    """
    return re.sub(r'[^a-zA-Z0-9_\-]', '', s)

def make_url_friendly(s: str):
    """
        Convert a string into a "URL-friendly" form.

        Steps:
            1. Remove all characters except alphanumerics, underscores, and dashes.
            2. Convert to lowercase, replace spaces with dashes, and strip quotes.

        Args:
            s (str): Input string.

        Returns:
            str: A URL-safe version of the string.
        """
    return slugify(strip_non_basic_characters(s))
