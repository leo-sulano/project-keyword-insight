import os
import logging
import pandas as pd
from datetime import datetime
from config import SITES, START_DATE, END_DATE, COUNTRIES, MIN_IMPRESSIONS, OUTPUT_DIR, LATEST_CSV
from auth import get_service
from gsc_client import fetch_site_data
from filters import filter_keywords

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse per-date rows into a site/keyword/country summary.

    Position is weighted by impressions so high-traffic days influence the
    average more than low-traffic days.
    """
    if df.empty:
        return df

    def _weighted_position(group: pd.DataFrame) -> float:
        total = group["impressions"].sum()
        if total == 0:
            return group["position"].mean()
        return (group["position"] * group["impressions"]).sum() / total

    keys = ["site", "keyword", "country"]

    sums = df.groupby(keys, as_index=False).agg(
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
    )

    pos = df.groupby(keys).apply(_weighted_position).reset_index()
    pos.columns = keys + ["avg_position"]

    result = sums.merge(pos, on=keys)
    result["ctr"] = (result["clicks"] / result["impressions"] * 100).round(2)
    result["avg_position"] = result["avg_position"].round(1)

    result = result[result["impressions"] >= MIN_IMPRESSIONS]
    return result.sort_values("clicks", ascending=False).reset_index(drop=True)


def run_pipeline() -> pd.DataFrame:
    """Run the full pipeline: fetch → filter → aggregate → export CSV."""
    service = get_service()
    all_rows: list[dict] = []

    for site in SITES:
        logger.info("Fetching  %s", site)
        try:
            rows = fetch_site_data(service, site, START_DATE, END_DATE, COUNTRIES)
            if rows:
                all_rows.extend(rows)
                logger.info("  collected %d rows", len(rows))
            else:
                logger.info("  no data returned")
        except Exception as exc:
            logger.error("Unhandled error for %s: %s", site, exc)

    if not all_rows:
        logger.warning("No data collected from any site.")
        return pd.DataFrame()

    raw = pd.DataFrame(all_rows)
    filtered = filter_keywords(raw)
    logger.info(
        "Filtering: %d raw rows → %d after brand/nav removal",
        len(raw),
        len(filtered),
    )

    result = aggregate(filtered)
    logger.info("Aggregated to %d unique keyword rows", len(result))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"gsc_nonbranded_{ts}.csv")
    result.to_csv(csv_path, index=False)
    result.to_csv(LATEST_CSV, index=False)
    logger.info("Saved → %s (also → %s)", csv_path, LATEST_CSV)

    return result


if __name__ == "__main__":
    df = run_pipeline()
    if not df.empty:
        print("\n=== Top 20 Non-Branded Keywords ===")
        print(
            df[["site", "keyword", "country", "clicks", "impressions", "ctr", "avg_position"]]
            .head(20)
            .to_string(index=False)
        )
