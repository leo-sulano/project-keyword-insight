import time
import logging
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

MAX_ROWS = 25000
_REQUEST_DELAY = 0.5   # seconds between paginated requests


def fetch_site_data(
    service,
    site_url: str,
    start_date: str,
    end_date: str,
    countries: list[str],
) -> list[dict]:
    """Fetch all GSC rows for one site, one country at a time.

    Args:
        service:    Authenticated Search Console API service (from auth.get_service).
        site_url:   The GSC property URL, e.g. "https://example.com/".
        start_date: ISO date string, e.g. "2026-01-01".
        end_date:   ISO date string, e.g. "2026-04-30".
        countries:  ISO 3166-1 alpha-3 country codes to fetch, e.g. ["SAU", "KWT"].
                    One API call series is made per country.

    Returns:
        List of row dicts with keys: site, keyword, country, date,
        clicks, impressions, ctr, position.

    Per-site HTTP errors are handled internally so one inaccessible property
    never aborts the full pipeline.  429 and 5xx errors are retried with backoff.
    """
    all_rows: list[dict] = []

    for country in countries:
        offset = 0
        while True:
            try:
                response = (
                    service.searchanalytics()
                    .query(
                        siteUrl=site_url,
                        body={
                            "startDate": start_date,
                            "endDate": end_date,
                            "dimensions": ["query", "country", "date"],
                            "dimensionFilterGroups": [{
                                "filters": [{
                                    "dimension": "country",
                                    "operator": "equals",
                                    "expression": country.lower(),
                                }]
                            }],
                            "rowLimit": MAX_ROWS,
                            "startRow": offset,
                        },
                    )
                    .execute()
                )
            except HttpError as exc:
                status = exc.resp.status
                if status == 429:
                    logger.warning("Rate limited on %s — waiting 60 s then retrying", site_url)
                    time.sleep(60)
                    continue
                elif status in (500, 502, 503, 504):
                    logger.warning("Transient %s on %s — waiting 30 s then retrying", status, site_url)
                    time.sleep(30)
                    continue
                elif status == 403:
                    logger.warning("No GSC access to %s (403 Forbidden) — skipping", site_url)
                elif status == 404:
                    logger.warning("Site not found in GSC: %s — skipping", site_url)
                else:
                    logger.error("API error for %s: %s", site_url, exc)
                # Site-level error — no point trying other countries
                return all_rows

            rows = response.get("rows", [])
            if not rows:
                break

            for row in rows:
                all_rows.append(
                    {
                        "site": site_url,
                        "keyword": row["keys"][0],
                        "country": row["keys"][1],
                        "date": row["keys"][2],
                        "clicks": row["clicks"],
                        "impressions": row["impressions"],
                        "ctr": row["ctr"],
                        "position": row["position"],
                    }
                )

            if len(rows) < MAX_ROWS:
                break

            offset += MAX_ROWS
            time.sleep(_REQUEST_DELAY)

    return all_rows
