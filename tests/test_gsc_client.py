import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import MagicMock, patch
from gsc_client import fetch_site_data


def _make_service(pages: list[dict]):
    """Build a mock GSC service that yields pages sequentially."""
    mock_query = MagicMock()
    mock_query.execute.side_effect = pages
    mock_sa = MagicMock()
    mock_sa.query.return_value = mock_query
    service = MagicMock()
    service.searchanalytics.return_value = mock_sa
    return service


def test_fetch_single_page_returns_rows():
    page = {
        "rows": [
            {
                "keys": ["slot games", "sau", "2026-04-01"],
                "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 5.0,
            }
        ]
    }
    service = _make_service([page, {}])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])
    assert len(result) == 1
    assert result[0]["keyword"] == "slot games"
    assert result[0]["clicks"] == 10
    assert result[0]["site"] == "https://example.com"


def test_fetch_empty_response_returns_empty_list():
    service = _make_service([{}])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])
    assert result == []


def test_fetch_multiple_countries_returns_combined():
    page_sau = {"rows": [{"keys": ["casino", "sau", "2026-04-01"], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 3.0}]}
    page_kwt = {"rows": [{"keys": ["slots", "kwt", "2026-04-01"], "clicks": 3, "impressions": 30, "ctr": 0.1, "position": 4.0}]}
    # Each page has 1 row (< MAX_ROWS), so the while-loop breaks immediately after
    # collecting it — no second execute() call per country.
    service = _make_service([page_sau, page_kwt])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU", "KWT"])
    assert len(result) == 2
    countries = {r["country"] for r in result}
    assert countries == {"sau", "kwt"}


def test_fetch_http_403_skips_silently():
    from googleapiclient.errors import HttpError
    resp = MagicMock()
    resp.status = 403
    error = HttpError(resp=resp, content=b"Forbidden")

    mock_query = MagicMock()
    mock_query.execute.side_effect = error
    mock_sa = MagicMock()
    mock_sa.query.return_value = mock_query
    service = MagicMock()
    service.searchanalytics.return_value = mock_sa

    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])
    assert result == []


def test_fetch_pagination_stops_below_max():
    rows_page1 = [
        {"keys": [f"keyword{i}", "sau", "2026-04-01"], "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 5.0}
        for i in range(100)
    ]
    page1 = {"rows": rows_page1}
    service = _make_service([page1, {}])

    with patch("gsc_client.MAX_ROWS", 25000):
        result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])

    assert len(result) == 100
