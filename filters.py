import re
import pandas as pd
from config import BRAND_TERMS, NAVIGATIONAL_TERMS


def _build_pattern(terms: list[str]) -> re.Pattern:
    # Sort longest first so more specific phrases match before substrings
    escaped = sorted([re.escape(t) for t in terms], key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)


_FILTER_PATTERN = _build_pattern(BRAND_TERMS + NAVIGATIONAL_TERMS)

_ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿ]")
_LATIN_RE = re.compile(r"[a-zA-Z]")


def is_branded(keyword: str) -> bool:
    """Return True if keyword contains any brand or navigational term."""
    return bool(_FILTER_PATTERN.search(keyword))


def detect_language(keyword: str) -> str:
    """Return 'ar' for Arabic, 'en' for Latin-script, 'other' otherwise."""
    if _ARABIC_RE.search(keyword):
        return "ar"
    if _LATIN_RE.search(keyword):
        return "en"
    return "other"


def filter_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise keywords to lowercase, strip whitespace, remove branded rows."""
    df = df.copy()
    df["keyword"] = df["keyword"].str.lower().str.strip()
    mask = ~df["keyword"].apply(is_branded)
    return df[mask].reset_index(drop=True)


def add_language_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'language' column ('ar', 'en', or 'other') based on keyword script."""
    df = df.copy()
    df["language"] = df["keyword"].apply(detect_language)
    return df
