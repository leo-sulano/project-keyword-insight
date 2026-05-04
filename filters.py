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
    if not isinstance(keyword, str):
        return False
    return bool(_FILTER_PATTERN.search(keyword))


def detect_language(keyword: str) -> str:
    """Return 'ar' for Arabic, 'en' for Latin-script, 'other' otherwise."""
    if not isinstance(keyword, str):
        return "other"
    if _ARABIC_RE.search(keyword):
        return "ar"
    if _LATIN_RE.search(keyword):
        return "en"
    return "other"


def filter_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise keywords and remove branded rows entirely.

    Used by the Streamlit dashboard's live-fetch path where only non-branded
    rows are needed immediately, without retaining the branded flag.
    """
    df = df.copy()
    df["keyword"] = df["keyword"].str.lower().str.strip()
    mask = ~df["keyword"].apply(is_branded)
    return df[mask].reset_index(drop=True)


def mark_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise keywords and add a 'branded' boolean column. Keeps all rows.

    Used by the pipeline so branded rows can be logged/counted before being
    dropped in run_pipeline(), and so aggregate() can report both groups.
    """
    df = df.copy()
    df["keyword"] = df["keyword"].str.lower().str.strip()
    df["branded"] = df["keyword"].apply(is_branded)
    return df.reset_index(drop=True)


def add_language_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'language' column ('ar', 'en', or 'other') based on keyword script."""
    df = df.copy()
    df["language"] = df["keyword"].apply(detect_language)
    return df
