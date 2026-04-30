# GSC Non-Branded Keyword Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python data pipeline that extracts non-branded keywords from 27 websites via the Google Search Console API, filtered to Saudi Arabia and Kuwait, and presents results in an interactive Streamlit dashboard.

**Architecture:** A layered pipeline — `config.py` holds all editable parameters, `auth.py` manages OAuth2 tokens, `gsc_client.py` handles paginated API calls with rate-limit handling, `filters.py` applies brand/navigational filtering, `pipeline.py` orchestrates the full run and writes CSVs, and `dashboard.py` is the Streamlit frontend. Tests live in `tests/` and cover filtering logic and pipeline aggregation.

**Tech Stack:** Python 3.11+, google-api-python-client, google-auth-oauthlib, pandas, streamlit, plotly

---

## File Map

| File | Responsibility |
|------|----------------|
| `config.py` | All editable parameters: sites, dates, brand terms, countries, thresholds |
| `auth.py` | Google OAuth2 flow — token persistence, refresh, service object creation |
| `gsc_client.py` | Single-site GSC API calls with pagination and per-status error handling |
| `filters.py` | Brand/navigational regex filter; DataFrame normalization |
| `pipeline.py` | Orchestrator: loops sites → fetches → filters → aggregates → writes CSV |
| `dashboard.py` | Streamlit app: sidebar filters, KPI cards, table, charts |
| `requirements.txt` | Pinned dependencies |
| `.gitignore` | Excludes credentials/, output/, __pycache__ |
| `tests/test_filters.py` | Unit tests for filtering logic |
| `tests/test_pipeline.py` | Unit tests for aggregation logic |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `credentials/.gitkeep`
- Create: `output/.gitkeep`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.1
google-auth-oauthlib>=1.1.0
pandas>=2.0.0
streamlit>=1.32.0
plotly>=5.20.0
pytest>=8.0.0
langdetect>=1.0.9
```

- [ ] **Step 2: Create .gitignore**

```
credentials/client_secrets.json
credentials/token.pickle
output/
__pycache__/
*.pyc
.env
.DS_Store
```

- [ ] **Step 3: Create supporting directories**

```bash
mkdir -p credentials output tests
touch credentials/.gitkeep output/.gitkeep tests/__init__.py
```

- [ ] **Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without error. Python 3.11+ required.

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt .gitignore credentials/.gitkeep output/.gitkeep tests/__init__.py
git commit -m "chore: scaffold project structure and dependencies"
```

---

## Task 2: Configuration Module

**Files:**
- Create: `config.py`

- [ ] **Step 1: Write failing test for config imports**

Create `tests/test_config.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def test_sites_list_length():
    assert len(config.SITES) == 27


def test_countries_filter():
    assert config.COUNTRIES == ["SAU", "KWT"]


def test_min_impressions_positive():
    assert config.MIN_IMPRESSIONS > 0


def test_brand_terms_nonempty():
    assert len(config.BRAND_TERMS) >= 10
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Create config.py**

```python
SITES = [
    "https://lucky7evencasino.com",
    "https://lucky7evencasino.org",
    "http://lucky7evencasino.io",
    "https://fortuneplaycasino.net",
    "https://fortuneplay.casino/",
    "https://fortuneplay.io",
    "https://www.spinjo.io",
    "https://www.spinjocasino.com",
    "https://www.casinospinjo.com",
    "https://roosters.bet",
    "https://roostersbet.com",
    "https://casinoroosters.com",
    "https://www.spinsup.io/",
    "https://spinsupcasino.com/",
    "https://casinospinsup.com/",
    "https://rollero.io/",
    "https://rollerocasino.com/",
    "https://www.casinorollero.com/",
    "https://rocketspin.io/",
    "https://rocketspincasino.com/",
    "https://www.casinorocketspin.com/",
    "https://www.playmojo.io/",
    "https://www.playmojocasino.com/",
    "https://casinoplaymojo.com/",
    "https://www.luckyvibe.io/",
    "https://www.luckyvibecasino.com",
    "https://www.casinoluckyvibe.com",
]

START_DATE = "2026-04-01"
END_DATE = "2026-04-30"
COUNTRIES = ["SAU", "KWT"]

BRAND_TERMS = [
    # lucky7even brand
    "lucky7even", "lucky7", "lucky 7 even", "lucky 7even", "lucky seven casino",
    # fortuneplay brand
    "fortuneplay", "fortune play", "fortuneplay casino", "fortune play casino",
    # spinjo brand
    "spinjo", "spin jo", "spinjo casino", "spin jo casino",
    # roosters brand
    "roosters", "roostersbet", "roosters bet", "roosters casino", "casinoroosters",
    # spinsup brand
    "spinsup", "spin sup", "spins up", "spinsupcasino", "spinsup casino",
    # rollero brand
    "rollero", "rollero casino", "rollerocasino", "casinorollero",
    # rocketspin brand
    "rocketspin", "rocket spin", "rocketspin casino", "rocket spin casino", "casinorocketspin",
    # playmojo brand
    "playmojo", "play mojo", "playmojo casino", "play mojo casino", "casinoplaymojo",
    # luckyvibe brand
    "luckyvibe", "lucky vibe", "luckyvibe casino", "lucky vibe casino", "casinoluckyvibe",
]

NAVIGATIONAL_TERMS = [
    "login", "log in", "register", "sign up", "signup",
    "homepage", "home page", "official site", "official website",
    "download", "mobile app",
]

MIN_IMPRESSIONS = 10

CREDENTIALS_FILE = "credentials/client_secrets.json"
TOKEN_FILE = "credentials/token.pickle"
OUTPUT_DIR = "output"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add configuration module with all sites and brand terms"
```

---

## Task 3: Brand Filtering Logic

**Files:**
- Create: `filters.py`
- Create: `tests/test_filters.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_filters.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import pytest
from filters import is_branded, filter_keywords


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


def test_filter_df_removes_branded():
    df = pd.DataFrame({
        "site": ["https://spinjo.io", "https://spinjo.io"],
        "keyword": ["spinjo login", "best online casino"],
        "country": ["SAU", "SAU"],
        "clicks": [10, 50],
        "impressions": [100, 500],
        "ctr": [0.1, 0.1],
        "position": [5.0, 3.0],
        "date": ["2026-04-01", "2026-04-01"],
    })
    result = filter_keywords(df)
    assert len(result) == 1
    assert result.iloc[0]["keyword"] == "best online casino"


def test_filter_df_normalizes_to_lowercase():
    df = pd.DataFrame({
        "site": ["https://example.com"],
        "keyword": ["Best Online Casino"],
        "country": ["SAU"],
        "clicks": [10],
        "impressions": [100],
        "ctr": [0.1],
        "position": [5.0],
        "date": ["2026-04-01"],
    })
    result = filter_keywords(df)
    assert result.iloc[0]["keyword"] == "best online casino"


def test_filter_df_strips_whitespace():
    df = pd.DataFrame({
        "site": ["https://example.com"],
        "keyword": ["  slot games  "],
        "country": ["KWT"],
        "clicks": [5],
        "impressions": [50],
        "ctr": [0.1],
        "position": [8.0],
        "date": ["2026-04-01"],
    })
    result = filter_keywords(df)
    assert result.iloc[0]["keyword"] == "slot games"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_filters.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'filters'`

- [ ] **Step 3: Create filters.py**

```python
import re
import pandas as pd
from config import BRAND_TERMS, NAVIGATIONAL_TERMS


def _build_pattern(terms: list[str]) -> re.Pattern:
    escaped = sorted([re.escape(t) for t in terms], key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)


_FILTER_PATTERN = _build_pattern(BRAND_TERMS + NAVIGATIONAL_TERMS)


def is_branded(keyword: str) -> bool:
    return bool(_FILTER_PATTERN.search(keyword))


def filter_keywords(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["keyword"] = df["keyword"].str.lower().str.strip()
    mask = ~df["keyword"].apply(is_branded)
    return df[mask].reset_index(drop=True)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_filters.py -v
```

Expected: 10 PASSED

- [ ] **Step 5: Commit**

```bash
git add filters.py tests/test_filters.py
git commit -m "feat: add brand/navigational keyword filter with regex pattern"
```

---

## Task 4: GSC Authentication Module

**Files:**
- Create: `auth.py`

No unit tests here — OAuth2 requires live credentials. Manual verification in Task 6.

- [ ] **Step 1: Create auth.py**

```python
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import CREDENTIALS_FILE, TOKEN_FILE, SCOPES


def get_service():
    """Return an authenticated Search Console API service object.

    On first run opens a browser for OAuth2 consent. Subsequent runs load
    the persisted token from TOKEN_FILE and refresh it if expired.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as fh:
            creds = pickle.load(fh)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"OAuth credentials not found at '{CREDENTIALS_FILE}'.\n"
                    "Download client_secrets.json from Google Cloud Console and place it there."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "wb") as fh:
            pickle.dump(creds, fh)

    return build("searchconsole", "v1", credentials=creds)
```

- [ ] **Step 2: Commit**

```bash
git add auth.py
git commit -m "feat: add OAuth2 authentication module for GSC API"
```

---

## Task 5: GSC API Client with Pagination

**Files:**
- Create: `gsc_client.py`
- Create: `tests/test_gsc_client.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_gsc_client.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from unittest.mock import MagicMock, patch, call
from gsc_client import fetch_site_data


def _make_service(pages):
    """Build a mock service that returns pages sequentially."""
    mock_query = MagicMock()
    mock_query.execute.side_effect = pages
    mock_sa = MagicMock()
    mock_sa.query.return_value = mock_query
    service = MagicMock()
    service.searchanalytics.return_value = mock_sa
    return service


def test_fetch_single_page():
    page = {
        "rows": [
            {"keys": ["slot games", "sau", "2026-04-01"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 5.0}
        ]
    }
    service = _make_service([page, {}])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])
    assert len(result) == 1
    assert result[0]["keyword"] == "slot games"
    assert result[0]["clicks"] == 10


def test_fetch_empty_response():
    service = _make_service([{}])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])
    assert result == []


def test_fetch_multiple_countries():
    page_sau = {"rows": [{"keys": ["casino", "sau", "2026-04-01"], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 3.0}]}
    page_kwt = {"rows": [{"keys": ["slots", "kwt", "2026-04-01"], "clicks": 3, "impressions": 30, "ctr": 0.1, "position": 4.0}]}
    service = _make_service([page_sau, {}, page_kwt, {}])
    result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU", "KWT"])
    assert len(result) == 2
    countries = {r["country"] for r in result}
    assert countries == {"sau", "kwt"}


def test_fetch_http_403_skips_site():
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


def test_fetch_pagination_stops_when_less_than_max():
    rows_page1 = [
        {"keys": [f"keyword{i}", "sau", "2026-04-01"], "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 5.0}
        for i in range(100)
    ]
    page1 = {"rows": rows_page1}
    service = _make_service([page1, {}])

    with patch("gsc_client.MAX_ROWS", 25000):
        result = fetch_site_data(service, "https://example.com", "2026-04-01", "2026-04-30", ["SAU"])

    assert len(result) == 100
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_gsc_client.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'gsc_client'`

- [ ] **Step 3: Create gsc_client.py**

```python
import time
import logging
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

MAX_ROWS = 25000
_RATE_LIMIT_DELAY = 0.5


def fetch_site_data(
    service,
    site_url: str,
    start_date: str,
    end_date: str,
    countries: list[str],
) -> list[dict]:
    """Fetch all rows for a single site across requested countries.

    Handles pagination via startRow and catches HTTP errors per site so one
    inaccessible property does not abort the entire pipeline.
    """
    all_rows = []

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
                            "dimensionFilterGroups": [
                                {
                                    "filters": [
                                        {
                                            "dimension": "country",
                                            "operator": "equals",
                                            "expression": country,
                                        }
                                    ]
                                }
                            ],
                            "rowLimit": MAX_ROWS,
                            "startRow": offset,
                        },
                    )
                    .execute()
                )
            except HttpError as exc:
                if exc.resp.status == 429:
                    logger.warning("Rate limited on %s — sleeping 60 s", site_url)
                    time.sleep(60)
                    continue
                elif exc.resp.status == 403:
                    logger.warning("No GSC access to %s (403)", site_url)
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
            time.sleep(_RATE_LIMIT_DELAY)

    return all_rows
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_gsc_client.py -v
```

Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add gsc_client.py tests/test_gsc_client.py
git commit -m "feat: add GSC API client with pagination and per-status error handling"
```

---

## Task 6: Pipeline Orchestrator

**Files:**
- Create: `pipeline.py`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_pipeline.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pipeline import aggregate, run_pipeline


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
    sau_slot = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    assert sau_slot["clicks"].values[0] == 30


def test_aggregate_sums_impressions():
    result = aggregate(_raw_df())
    sau_slot = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    assert sau_slot["impressions"].values[0] == 300


def test_aggregate_weighted_position():
    result = aggregate(_raw_df())
    sau_slot = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    # weighted: (3.0*100 + 5.0*200) / 300 = 1300/300 = 4.333... -> rounds to 4.3
    assert sau_slot["avg_position"].values[0] == 4.3


def test_aggregate_computes_ctr():
    result = aggregate(_raw_df())
    sau_slot = result[(result["keyword"] == "slot games") & (result["country"] == "SAU")]
    expected_ctr = round(30 / 300 * 100, 2)
    assert sau_slot["ctr"].values[0] == expected_ctr


def test_aggregate_filters_low_impressions():
    df = _raw_df()
    df.loc[df["keyword"] == "poker tips", "impressions"] = 2
    result = aggregate(df)
    assert "poker tips" not in result["keyword"].values


def test_run_pipeline_empty_returns_empty_df(tmp_path):
    with patch("pipeline.get_service", return_value=MagicMock()), \
         patch("pipeline.fetch_site_data", return_value=[]), \
         patch("pipeline.SITES", ["https://example.com"]), \
         patch("pipeline.OUTPUT_DIR", str(tmp_path)):
        result = run_pipeline()
    assert isinstance(result, pd.DataFrame)
    assert result.empty
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_pipeline.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline'`

- [ ] **Step 3: Create pipeline.py**

```python
import os
import logging
import pandas as pd
from datetime import datetime
from config import SITES, START_DATE, END_DATE, COUNTRIES, MIN_IMPRESSIONS, OUTPUT_DIR
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
    """Aggregate raw per-date rows into site/keyword/country summary."""
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
    service = get_service()
    all_rows: list[dict] = []

    for site in SITES:
        logger.info("Fetching %s", site)
        try:
            rows = fetch_site_data(service, site, START_DATE, END_DATE, COUNTRIES)
            if rows:
                all_rows.extend(rows)
                logger.info("  %d rows collected", len(rows))
            else:
                logger.info("  No data")
        except Exception as exc:
            logger.error("Failed for %s: %s", site, exc)

    if not all_rows:
        logger.warning("No data collected from any site.")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = filter_keywords(df)

    result = aggregate(df)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(OUTPUT_DIR, f"gsc_nonbranded_{ts}.csv")
    result.to_csv(csv_path, index=False)
    logger.info("Saved %d rows → %s", len(result), csv_path)

    return result


if __name__ == "__main__":
    df = run_pipeline()
    print(df.to_string())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_pipeline.py -v
```

Expected: 6 PASSED

- [ ] **Step 5: Run all tests to verify nothing broken**

```bash
pytest -v
```

Expected: All tests PASSED (config + filters + gsc_client + pipeline)

- [ ] **Step 6: Commit**

```bash
git add pipeline.py tests/test_pipeline.py
git commit -m "feat: add pipeline orchestrator with weighted-position aggregation and CSV export"
```

---

## Task 7: GSC API Authentication Setup (Manual)

This task is done by the user before running the pipeline. No code changes.

- [ ] **Step 1: Enable Google Search Console API**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services → Library**
4. Search **"Google Search Console API"** → Enable it

- [ ] **Step 2: Create OAuth 2.0 credentials**

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Name it anything (e.g., `GSC Pipeline`)
5. Click **Create**
6. Click **Download JSON**
7. Save the file as `credentials/client_secrets.json` inside this project

- [ ] **Step 3: Add GSC properties to your account**

Each site in `config.py` must be added as a **Property** in your Google Search Console account at [search.google.com/search-console](https://search.google.com/search-console). Unverified properties will return 403 errors (skipped automatically).

- [ ] **Step 4: First-run authentication**

```bash
python pipeline.py
```

A browser window will open. Log in with the Google account that has GSC access. After consent the token is saved to `credentials/token.pickle` and the pipeline runs automatically.

---

## Task 8: Streamlit Dashboard

**Files:**
- Create: `dashboard.py`

- [ ] **Step 1: Create dashboard.py**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob
from datetime import datetime

from config import SITES, START_DATE, END_DATE, COUNTRIES, MIN_IMPRESSIONS
from auth import get_service
from gsc_client import fetch_site_data
from filters import filter_keywords
from pipeline import aggregate

st.set_page_config(
    page_title="GSC Non-Branded Keywords",
    page_icon="🔍",
    layout="wide",
)


# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_data(
    sites: tuple[str, ...],
    start_date: str,
    end_date: str,
    countries: tuple[str, ...],
) -> pd.DataFrame:
    service = get_service()
    all_rows: list[dict] = []
    progress = st.progress(0, text="Fetching GSC data…")

    for i, site in enumerate(sites):
        try:
            rows = fetch_site_data(service, site, start_date, end_date, list(countries))
            all_rows.extend(rows)
        except Exception as exc:
            st.warning(f"Skipped {site}: {exc}")
        progress.progress((i + 1) / len(sites), text=f"Fetched {i + 1}/{len(sites)} sites")

    progress.empty()

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = filter_keywords(df)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_from_csv() -> pd.DataFrame:
    files = sorted(glob.glob("output/gsc_nonbranded_*.csv"), reverse=True)
    if not files:
        return pd.DataFrame()
    return pd.read_csv(files[0])


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Filters")

    data_source = st.radio("Data source", ["Fetch live from GSC", "Load latest CSV"])

    selected_sites = st.multiselect(
        "Sites",
        SITES,
        default=SITES[:5],
        help="Leave empty to select all",
    )
    if not selected_sites:
        selected_sites = SITES

    selected_countries = st.multiselect(
        "Countries",
        ["SAU", "KWT"],
        default=["SAU", "KWT"],
    )

    col_s, col_e = st.columns(2)
    start = col_s.date_input("Start", value=pd.to_datetime(START_DATE))
    end = col_e.date_input("End", value=pd.to_datetime(END_DATE))

    fetch_btn = st.button("🔄 Fetch / Reload", use_container_width=True)

    if fetch_btn:
        st.cache_data.clear()


# ── Load data ──────────────────────────────────────────────────────────────────

if data_source == "Fetch live from GSC":
    with st.spinner("Connecting to GSC API…"):
        raw_df = load_data(
            tuple(selected_sites),
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
            tuple(selected_countries),
        )
else:
    raw_df = load_from_csv()

if raw_df.empty:
    st.warning("No data available. Run `python pipeline.py` first or fetch live data.")
    st.stop()

agg_df = aggregate(raw_df) if "date" in raw_df.columns else raw_df


# ── KPI Cards ──────────────────────────────────────────────────────────────────

st.title("📊 GSC Non-Branded Keywords — SAU & KWT")
st.caption(f"Date range: {start} → {end}  |  {len(agg_df):,} keyword rows")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Clicks", f"{agg_df['clicks'].sum():,}")
k2.metric("Total Impressions", f"{agg_df['impressions'].sum():,}")
k3.metric("Avg CTR", f"{agg_df['ctr'].mean():.2f}%")
k4.metric("Avg Position", f"{agg_df['avg_position'].mean():.1f}")


# ── Top Keywords Table ──────────────────────────────────────────────────────────

st.subheader("Top Non-Branded Keywords")
display_cols = ["site", "keyword", "country", "clicks", "impressions", "ctr", "avg_position"]
available = [c for c in display_cols if c in agg_df.columns]
st.dataframe(
    agg_df[available].head(200),
    use_container_width=True,
    column_config={
        "ctr": st.column_config.NumberColumn("CTR %", format="%.2f"),
        "avg_position": st.column_config.NumberColumn("Avg Pos", format="%.1f"),
    },
)

csv_bytes = agg_df.to_csv(index=False).encode()
st.download_button("⬇️ Download CSV", csv_bytes, "gsc_keywords.csv", "text/csv")


# ── Country Comparison ─────────────────────────────────────────────────────────

st.subheader("Country Comparison — SAU vs KWT")
country_agg = agg_df.groupby("country", as_index=False).agg(
    clicks=("clicks", "sum"),
    impressions=("impressions", "sum"),
)
fig_country = px.bar(
    country_agg,
    x="country",
    y=["clicks", "impressions"],
    barmode="group",
    color_discrete_sequence=["#4F46E5", "#10B981"],
    labels={"value": "Count", "variable": "Metric"},
)
st.plotly_chart(fig_country, use_container_width=True)


# ── Time Series ────────────────────────────────────────────────────────────────

if "date" in raw_df.columns:
    st.subheader("Clicks & Impressions Over Time")
    time_agg = (
        raw_df.groupby("date", as_index=False)
        .agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
    )
    fig_time = px.line(
        time_agg,
        x="date",
        y=["clicks", "impressions"],
        color_discrete_sequence=["#4F46E5", "#10B981"],
        labels={"value": "Count", "variable": "Metric"},
    )
    st.plotly_chart(fig_time, use_container_width=True)


# ── CTR vs Position Scatter ────────────────────────────────────────────────────

st.subheader("CTR vs Average Position")
fig_scatter = px.scatter(
    agg_df.head(300),
    x="avg_position",
    y="ctr",
    size="impressions",
    color="country" if "country" in agg_df.columns else None,
    hover_data=["keyword", "site", "clicks"],
    color_discrete_sequence=["#4F46E5", "#F59E0B"],
    labels={"avg_position": "Avg Position", "ctr": "CTR %"},
    title="Bubble size = Impressions",
)
fig_scatter.update_layout(xaxis={"autorange": "reversed"})
st.plotly_chart(fig_scatter, use_container_width=True)


# ── Opportunity Keywords ───────────────────────────────────────────────────────

st.subheader("🎯 Opportunity Keywords (High Impressions, Low CTR)")
threshold_impressions = st.slider("Min Impressions", 50, 5000, 200, step=50)
threshold_ctr = st.slider("Max CTR %", 0.1, 10.0, 2.0, step=0.1)

opps = agg_df[
    (agg_df["impressions"] >= threshold_impressions) & (agg_df["ctr"] <= threshold_ctr)
].sort_values("impressions", ascending=False)

st.dataframe(opps[available].head(100), use_container_width=True)
```

- [ ] **Step 2: Run the dashboard locally**

```bash
streamlit run dashboard.py
```

Expected: Browser opens at `http://localhost:8501`. Sidebar shows filter controls.

- [ ] **Step 3: Verify each panel renders**

Walk through the UI:
- Select 2–3 sites and click "Fetch / Reload"
- Confirm KPI cards show non-zero numbers after data loads
- Confirm table populates with lowercase keywords containing no brand terms
- Confirm country comparison bar chart renders
- Confirm time series renders (requires live fetch, not CSV)
- Confirm CTR vs Position scatter shows bubbles
- Confirm opportunity keywords table filters by sliders

- [ ] **Step 4: Commit**

```bash
git add dashboard.py
git commit -m "feat: add Streamlit dashboard with KPIs, charts, and opportunity filter"
```

---

## Task 9: Optional — Arabic/English Language Detection

**Files:**
- Modify: `filters.py` (add function)
- Modify: `dashboard.py` (add language column and filter)

- [ ] **Step 1: Add language detection to filters.py**

Add this function after the existing `filter_keywords` function:

```python
def detect_language(keyword: str) -> str:
    """Return 'ar' for Arabic, 'en' for English, 'other' otherwise."""
    arabic_pattern = re.compile(r"[؀-ۿ]")
    if arabic_pattern.search(keyword):
        return "ar"
    if re.search(r"[a-zA-Z]", keyword):
        return "en"
    return "other"


def add_language_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["language"] = df["keyword"].apply(detect_language)
    return df
```

- [ ] **Step 2: Write test for language detection**

Add to `tests/test_filters.py`:

```python
from filters import detect_language, add_language_column


def test_detect_arabic():
    assert detect_language("العاب قمار") == "ar"


def test_detect_english():
    assert detect_language("online casino") == "en"


def test_detect_mixed_arabic_english():
    assert detect_language("casino العاب") == "ar"


def test_add_language_column():
    df = pd.DataFrame({"keyword": ["slot games", "العاب قمار"]})
    result = add_language_column(df)
    assert list(result["language"]) == ["en", "ar"]
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_filters.py -v
```

Expected: All tests PASSED

- [ ] **Step 4: Add language filter to dashboard.py**

In the sidebar section (after `selected_countries`), add:

```python
selected_languages = st.multiselect(
    "Keyword Language",
    ["en", "ar", "other"],
    default=["en", "ar"],
)
```

After `agg_df = aggregate(...)`, add:

```python
from filters import add_language_column
agg_df = add_language_column(agg_df)
agg_df = agg_df[agg_df["language"].isin(selected_languages)]
```

- [ ] **Step 5: Commit**

```bash
git add filters.py dashboard.py tests/test_filters.py
git commit -m "feat: add Arabic/English language detection and dashboard filter"
```

---

## Task 10: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
pytest -v --tb=short
```

Expected: All tests PASSED. Zero failures.

- [ ] **Step 2: Run pipeline dry-run with a single mock site**

Create `test_run.py` temporarily:

```python
from unittest.mock import patch, MagicMock

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
     patch("pipeline.SITES", ["https://spinjo.io"]):
    from pipeline import run_pipeline
    df = run_pipeline()
    print(df.to_string())
    assert "spinjo login" not in df["keyword"].values, "Brand term not filtered!"
    assert "best online slots" in df["keyword"].values, "Non-branded term wrongly removed!"
    print("\nDry run PASSED")
```

```bash
python test_run.py
```

Expected output:
```
   site                keyword  country  clicks  impressions    ctr  avg_position
0  https://spinjo.io  best online slots    sau      20          300  6.67          4.2
1  https://spinjo.io  online casino bonus  kwt      15          200  7.50          6.1

Dry run PASSED
```

- [ ] **Step 3: Remove temporary test file**

```bash
rm test_run.py
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "chore: verify all tests pass and pipeline dry-run succeeds"
```

---

## Setup Instructions Summary

### 1. Install Python 3.11+

Download from [python.org](https://python.org) if not installed.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Google Cloud OAuth

Follow Task 7 above. Save `client_secrets.json` to `credentials/`.

### 4. Run the pipeline

```bash
python pipeline.py
```

First run opens a browser for OAuth consent. CSV saved to `output/`.

### 5. Run the dashboard

```bash
streamlit run dashboard.py
```

---

## Sample Output Schema

```
site,keyword,country,clicks,impressions,ctr,avg_position
https://spinjo.io,best online slots,sau,120,1800,6.67,4.2
https://spinjo.io,online casino games,kwt,85,1200,7.08,5.1
https://rollerocasino.com,casino bonus,sau,60,900,6.67,7.3
```

---

## Self-Review Checklist

| Spec Requirement | Task Covered |
|------------------|--------------|
| 27 sites looped | Task 2 config, Task 6 pipeline |
| SAU + KWT country filter | Task 5 gsc_client dimension filter |
| All brand terms excluded | Task 3 filters.py |
| Navigational terms excluded | Task 3 filters.py |
| impressions < 10 removed | Task 6 aggregate() |
| clicks, impressions, CTR, avg position | Task 6 aggregate() |
| Weighted avg position | Task 6 aggregate() |
| CSV output | Task 6 pipeline.py |
| Pagination | Task 5 gsc_client offset loop |
| Rate limit handling | Task 5 gsc_client 429 handler |
| Per-site error isolation | Task 5 gsc_client 403/other handler |
| KPI cards | Task 8 dashboard.py |
| Top keywords table | Task 8 dashboard.py |
| Country comparison chart | Task 8 dashboard.py |
| Time series | Task 8 dashboard.py |
| CTR vs Position scatter | Task 8 dashboard.py |
| Opportunity keywords | Task 8 dashboard.py |
| Language detection (optional) | Task 9 |
| All config editable | Task 2 config.py |
