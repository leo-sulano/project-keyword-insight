import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import pytest
from filters import is_branded, filter_keywords, detect_language, add_language_column


# ── is_branded ────────────────────────────────────────────────────────────────

def test_exact_brand_match():
    assert is_branded("spinjo") is True


def test_brand_as_substring():
    assert is_branded("spinjo casino bonus") is True


def test_brand_case_insensitive():
    assert is_branded("SpinJo Casino") is True


def test_navigational_login():
    assert is_branded("casino login") is True


def test_navigational_register():
    assert is_branded("register casino") is True


def test_generic_keyword_passes():
    assert is_branded("online casino slots") is False


def test_arabic_generic_passes():
    assert is_branded("العاب قمار اونلاين") is False


def test_luckyvibe_brand_caught():
    assert is_branded("luckyvibe review") is True


def test_rollero_brand_caught():
    assert is_branded("rollero casino bonus") is True


def test_rocketspin_brand_caught():
    assert is_branded("rocketspin free spins") is True


# ── filter_keywords ────────────────────────────────────────────────────────────

def _sample_df():
    return pd.DataFrame({
        "site": ["https://spinjo.io", "https://spinjo.io", "https://spinjo.io"],
        "keyword": ["spinjo login", "best online casino", "SLOT GAMES"],
        "country": ["SAU", "SAU", "KWT"],
        "clicks": [10, 50, 30],
        "impressions": [100, 500, 300],
        "ctr": [0.1, 0.1, 0.1],
        "position": [1.0, 3.0, 4.0],
        "date": ["2026-04-01", "2026-04-01", "2026-04-01"],
    })


def test_filter_df_removes_branded():
    result = filter_keywords(_sample_df())
    assert "spinjo login" not in result["keyword"].values


def test_filter_df_keeps_generic():
    result = filter_keywords(_sample_df())
    assert "best online casino" in result["keyword"].values


def test_filter_df_normalizes_to_lowercase():
    result = filter_keywords(_sample_df())
    assert "slot games" in result["keyword"].values


def test_filter_df_strips_whitespace():
    df = pd.DataFrame({
        "site": ["https://example.com"],
        "keyword": ["  slot games  "],
        "country": ["KWT"],
        "clicks": [5], "impressions": [50], "ctr": [0.1], "position": [8.0],
        "date": ["2026-04-01"],
    })
    result = filter_keywords(df)
    assert result.iloc[0]["keyword"] == "slot games"


def test_filter_df_resets_index():
    result = filter_keywords(_sample_df())
    assert list(result.index) == list(range(len(result)))


# ── detect_language ────────────────────────────────────────────────────────────

def test_detect_arabic():
    assert detect_language("العاب قمار") == "ar"


def test_detect_english():
    assert detect_language("online casino") == "en"


def test_detect_arabic_wins_over_latin():
    assert detect_language("casino العاب") == "ar"


# ── add_language_column ────────────────────────────────────────────────────────

def test_add_language_column():
    df = pd.DataFrame({"keyword": ["slot games", "العاب قمار"]})
    result = add_language_column(df)
    assert list(result["language"]) == ["en", "ar"]
