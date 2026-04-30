import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pipeline import aggregate


def _raw_df():
    return pd.DataFrame({
        "site": ["https://a.com"] * 4,
        "keyword": ["slot games", "slot games", "poker tips", "poker tips"],
        "country": ["SAU", "SAU", "KWT", "KWT"],
        "date": ["2026-04-01", "2026-04-02", "2026-04-01", "2026-04-02"],
        "clicks": [10, 20, 5, 15],
        "impressions": [100, 200, 50, 150],
        "ctr": [0.1, 0.1, 0.1, 0.1],
        "position": [3.0, 5.0, 2.0, 4.0],
    })


def test_aggregate_sums_clicks():
    result = aggregate(_raw_df())
    row = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    assert row["clicks"].values[0] == 30


def test_aggregate_sums_impressions():
    result = aggregate(_raw_df())
    row = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    assert row["impressions"].values[0] == 300


def test_aggregate_weighted_position():
    result = aggregate(_raw_df())
    row = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    # (3.0*100 + 5.0*200) / 300 = 1300/300 ≈ 4.333 → 4.3
    assert row["avg_position"].values[0] == 4.3


def test_aggregate_computes_ctr():
    result = aggregate(_raw_df())
    row = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    assert row["ctr"].values[0] == round(30 / 300 * 100, 2)


def test_aggregate_filters_low_impressions():
    df = _raw_df()
    df.loc[df["keyword"] == "poker tips", "impressions"] = 2
    result = aggregate(df)
    assert "poker tips" not in result["keyword"].values


def test_aggregate_returns_empty_for_empty_input():
    result = aggregate(pd.DataFrame())
    assert result.empty


def test_run_pipeline_returns_empty_when_no_data(tmp_path):
    with patch("pipeline.get_service", return_value=MagicMock()), \
         patch("pipeline.fetch_site_data", return_value=[]), \
         patch("pipeline.SITES", ["https://example.com"]), \
         patch("pipeline.OUTPUT_DIR", str(tmp_path)):
        from pipeline import run_pipeline
        result = run_pipeline()
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_run_pipeline_filters_brands_and_aggregates(tmp_path):
    mock_rows = [
        {"site": "https://spinjo.io", "keyword": "best online slots", "country": "sau",
         "date": "2026-04-10", "clicks": 20, "impressions": 300, "ctr": 0.067, "position": 4.2},
        {"site": "https://spinjo.io", "keyword": "spinjo login", "country": "sau",
         "date": "2026-04-10", "clicks": 5, "impressions": 100, "ctr": 0.05, "position": 1.0},
        {"site": "https://spinjo.io", "keyword": "online casino bonus", "country": "kwt",
         "date": "2026-04-10", "clicks": 15, "impressions": 200, "ctr": 0.075, "position": 6.1},
    ]
    with patch("pipeline.get_service", return_value=MagicMock()), \
         patch("pipeline.fetch_site_data", return_value=mock_rows), \
         patch("pipeline.SITES", ["https://spinjo.io"]), \
         patch("pipeline.OUTPUT_DIR", str(tmp_path)):
        from pipeline import run_pipeline
        result = run_pipeline()

    assert "spinjo login" not in result["keyword"].values, "Brand term should be filtered"
    assert "best online slots" in result["keyword"].values, "Generic term should pass"
    assert "online casino bonus" in result["keyword"].values, "Generic term should pass"
