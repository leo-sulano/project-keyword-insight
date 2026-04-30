import glob
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from config import COUNTRIES, END_DATE, LATEST_CSV, MIN_IMPRESSIONS, SITES, START_DATE
from filters import add_language_column, filter_keywords
from gsc_client import fetch_site_data
from pipeline import aggregate

st.set_page_config(
    page_title="GSC Non-Branded Keywords",
    page_icon="🔍",
    layout="wide",
)

# Bridge Streamlit secrets → env var so auth.py can find the service account
# in Streamlit Community Cloud without any code changes to auth.py.
if "GOOGLE_SERVICE_ACCOUNT_JSON" in st.secrets:
    os.environ.setdefault(
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"],
    )

_HAS_CREDENTIALS = bool(
    os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    or os.path.exists("credentials/token.pickle")
)


# ── Data helpers ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_live(
    sites: tuple[str, ...],
    start_date: str,
    end_date: str,
    countries: tuple[str, ...],
) -> pd.DataFrame:
    from auth import get_service  # imported here to avoid eager OAuth on page load
    service = get_service()
    all_rows: list[dict] = []
    prog = st.progress(0, text="Connecting to GSC API…")

    for i, site in enumerate(sites):
        try:
            rows = fetch_site_data(service, site, start_date, end_date, list(countries))
            all_rows.extend(rows)
        except Exception as exc:
            st.warning(f"Skipped {site}: {exc}")
        prog.progress((i + 1) / len(sites), text=f"Fetching site {i + 1}/{len(sites)}…")

    prog.empty()

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = filter_keywords(df)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _load_latest_csv() -> pd.DataFrame:
    # Prefer the fixed latest.csv written by the pipeline / GitHub Action
    if os.path.exists(LATEST_CSV):
        df = pd.read_csv(LATEST_CSV)
        st.caption(f"Loaded from: `{LATEST_CSV}`")
        return df
    # Fall back to newest timestamped file (local dev convenience)
    files = sorted(glob.glob("output/gsc_nonbranded_*.csv"), reverse=True)
    if not files:
        return pd.DataFrame()
    df = pd.read_csv(files[0])
    st.caption(f"Loaded from: `{files[0]}`")
    return df


# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⚙️ Filters")

    _source_options = ["Load latest CSV", "Fetch live from GSC"] if _HAS_CREDENTIALS else ["Load latest CSV"]
    data_source = st.radio(
        "Data source",
        _source_options,
        help="Live fetch requires GOOGLE_SERVICE_ACCOUNT_JSON or local OAuth token.",
    )

    selected_sites = st.multiselect("Sites", SITES, default=SITES[:5])
    if not selected_sites:
        selected_sites = SITES

    selected_countries = st.multiselect("Countries", ["SAU", "KWT"], default=["SAU", "KWT"])
    if not selected_countries:
        selected_countries = ["SAU", "KWT"]

    col_s, col_e = st.columns(2)
    start = col_s.date_input("Start", value=pd.to_datetime(START_DATE))
    end = col_e.date_input("End", value=pd.to_datetime(END_DATE))

    selected_languages = st.multiselect(
        "Keyword Language",
        ["en", "ar", "other"],
        default=["en", "ar"],
    )

    if st.button("🔄 Fetch / Reload", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ── Load ───────────────────────────────────────────────────────────────────────

if data_source == "Fetch live from GSC":
    with st.spinner("Fetching GSC data…"):
        raw_df = _fetch_live(
            tuple(selected_sites),
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
            tuple(selected_countries),
        )
else:
    raw_df = _load_latest_csv()

if raw_df.empty:
    st.warning(
        "No data available. Either run `python pipeline.py` to generate a CSV, "
        "or switch to **Fetch live from GSC** and click **Fetch / Reload**."
    )
    st.stop()

# Aggregate for table/KPIs; preserve raw for time series
agg_df = aggregate(raw_df) if "date" in raw_df.columns else raw_df.copy()

# Apply language filter
agg_df = add_language_column(agg_df)
if selected_languages:
    agg_df = agg_df[agg_df["language"].isin(selected_languages)]

# Apply country filter (CSV may have all countries)
if selected_countries:
    agg_df = agg_df[agg_df["country"].str.upper().isin([c.upper() for c in selected_countries])]


# ── KPI Cards ──────────────────────────────────────────────────────────────────

st.title("📊 GSC Non-Branded Keywords — SAU & KWT")
st.caption(
    f"Period: {start} → {end}  |  "
    f"{len(agg_df):,} keyword rows  |  "
    f"{agg_df['site'].nunique() if not agg_df.empty else 0} sites"
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Clicks", f"{int(agg_df['clicks'].sum()):,}")
k2.metric("Total Impressions", f"{int(agg_df['impressions'].sum()):,}")
avg_ctr = agg_df["ctr"].mean() if not agg_df.empty else 0
avg_pos = agg_df["avg_position"].mean() if not agg_df.empty else 0
k3.metric("Avg CTR", f"{avg_ctr:.2f}%")
k4.metric("Avg Position", f"{avg_pos:.1f}")


# ── Top Keywords Table ──────────────────────────────────────────────────────────

st.subheader("Top Non-Branded Keywords")

display_cols = ["site", "keyword", "country", "language", "clicks", "impressions", "ctr", "avg_position"]
available_cols = [c for c in display_cols if c in agg_df.columns]

st.dataframe(
    agg_df[available_cols].head(200),
    use_container_width=True,
    column_config={
        "ctr": st.column_config.NumberColumn("CTR %", format="%.2f"),
        "avg_position": st.column_config.NumberColumn("Avg Pos", format="%.1f"),
        "clicks": st.column_config.NumberColumn("Clicks", format="%d"),
        "impressions": st.column_config.NumberColumn("Impressions", format="%d"),
    },
)

csv_bytes = agg_df.to_csv(index=False).encode()
st.download_button("⬇️ Download CSV", csv_bytes, "gsc_nonbranded_keywords.csv", "text/csv")


# ── Country Comparison ─────────────────────────────────────────────────────────

st.subheader("Country Comparison — SAU vs KWT")

if not agg_df.empty:
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
        labels={"value": "Count", "variable": "Metric", "country": "Country"},
    )
    fig_country.update_layout(legend_title_text="")
    st.plotly_chart(fig_country, use_container_width=True)


# ── Time Series ────────────────────────────────────────────────────────────────

if "date" in raw_df.columns and not raw_df.empty:
    st.subheader("Clicks & Impressions Over Time")

    time_raw = raw_df.copy()
    if selected_countries:
        time_raw = time_raw[time_raw["country"].str.upper().isin([c.upper() for c in selected_countries])]

    time_agg = (
        time_raw.groupby("date", as_index=False)
        .agg(clicks=("clicks", "sum"), impressions=("impressions", "sum"))
    )

    fig_time = px.line(
        time_agg,
        x="date",
        y=["clicks", "impressions"],
        color_discrete_sequence=["#4F46E5", "#10B981"],
        labels={"value": "Count", "variable": "Metric", "date": "Date"},
    )
    fig_time.update_layout(legend_title_text="")
    st.plotly_chart(fig_time, use_container_width=True)


# ── CTR vs Position Scatter ────────────────────────────────────────────────────

if not agg_df.empty:
    st.subheader("CTR vs Average Position")

    fig_scatter = px.scatter(
        agg_df.head(300),
        x="avg_position",
        y="ctr",
        size="impressions",
        color="country" if "country" in agg_df.columns else None,
        hover_data=["keyword", "site", "clicks", "impressions"],
        color_discrete_sequence=["#4F46E5", "#F59E0B"],
        labels={
            "avg_position": "Avg Position",
            "ctr": "CTR %",
            "country": "Country",
        },
        title="Bubble size = Impressions",
    )
    # Lower position number = higher on results page, so reverse x-axis
    fig_scatter.update_layout(xaxis={"autorange": "reversed"})
    st.plotly_chart(fig_scatter, use_container_width=True)


# ── Opportunity Keywords ───────────────────────────────────────────────────────

st.subheader("🎯 Opportunity Keywords  (High Impressions · Low CTR)")
st.caption("Keywords ranking well but not converting clicks — quick SEO wins.")

col_imp, col_ctr = st.columns(2)
min_imp = col_imp.slider("Min Impressions", 50, 5000, 200, step=50)
max_ctr = col_ctr.slider("Max CTR %", 0.1, 10.0, 2.0, step=0.1)

if not agg_df.empty:
    opps = agg_df[
        (agg_df["impressions"] >= min_imp) & (agg_df["ctr"] <= max_ctr)
    ].sort_values("impressions", ascending=False)

    st.metric("Opportunity keywords found", len(opps))
    opp_cols = [c for c in display_cols if c in opps.columns]
    st.dataframe(
        opps[opp_cols].head(100),
        use_container_width=True,
        column_config={
            "ctr": st.column_config.NumberColumn("CTR %", format="%.2f"),
            "avg_position": st.column_config.NumberColumn("Avg Pos", format="%.1f"),
        },
    )
