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
) -> list[dict]:
    """Fetch all GSC rows for one site across all countries.

    Paginates via startRow until fewer than MAX_ROWS rows are returned.
    Per-site errors are caught so one inaccessible property never aborts
    the whole pipeline.
    """
    all_rows: list[dict] = []
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
                        "rowLimit": MAX_ROWS,
                        "startRow": offset,
                    },
                )
                .execute()
            )
        except HttpError as exc:
            if exc.resp.status == 429:
                logger.warning("Rate limited on %s — waiting 60 s then retrying", site_url)
                time.sleep(60)
                continue
            elif exc.resp.status == 403:
                logger.warning("No GSC access to %s (403 Forbidden) — skipping", site_url)
            elif exc.resp.status == 404:
                logger.warning("Site not found in GSC: %s — skipping", site_url)
            else:
                logger.error("API error for %s: %s", site_url, exc)
            break

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
