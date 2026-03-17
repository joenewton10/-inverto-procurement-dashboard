import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EU Procurement Benchmark",
    page_icon="📊",
    layout="wide",
)

# ── Contract type labels ──────────────────────────────────────────────────────
CONTRACT_TYPE_LABELS = {"S": "Services", "U": "Supplies", "W": "Works"}

# ── CPV top-level divisions (first 2 digits of 8-digit code) ─────────────────
CPV_DIVISIONS = {
    "03": "Agriculture & Forestry",
    "09": "Petroleum & Fuels",
    "14": "Mining & Quarrying",
    "15": "Food & Beverages",
    "16": "Agricultural Machinery",
    "18": "Clothing & Textiles",
    "19": "Leather & Rubber",
    "22": "Printed Matter",
    "24": "Chemicals",
    "30": "Office & Computing",
    "31": "Electrical Equipment",
    "32": "Radio & Telecom",
    "33": "Medical Equipment",
    "34": "Transport Equipment",
    "35": "Security Equipment",
    "37": "Musical & Sports",
    "38": "Lab & Optical",
    "39": "Furniture",
    "41": "Water",
    "42": "Industrial Machinery",
    "43": "Mining Machinery",
    "44": "Construction Materials",
    "45": "Construction Works",
    "48": "Software",
    "50": "Repair & Maintenance",
    "51": "Installation",
    "55": "Hotels & Restaurants",
    "60": "Transport Services",
    "63": "Freight & Logistics",
    "64": "Postal & Telecom",
    "65": "Gas & Water Supply",
    "66": "Financial Services",
    "70": "Real Estate",
    "71": "Architecture & Engineering",
    "72": "IT Services",
    "73": "R&D Services",
    "75": "Public Administration",
    "76": "Oil & Gas Services",
    "77": "Agriculture Services",
    "79": "Business Services",
    "80": "Education",
    "85": "Health & Social",
    "90": "Sewage & Waste",
    "92": "Recreation & Culture",
    "98": "Other Services",
}


@st.cache_resource
def load_data():
    needed_cols = [
        "DT_AWARD",
        "TYPE_OF_CONTRACT",
        "CPV",
        "ISO_COUNTRY_CODE",
        "WIN_COUNTRY_CODE",
        "AWARD_VALUE_EURO",
        "VALUE_EURO",
        "CAE_TYPE",
        "MAIN_ACTIVITY",
        "TITLE",
        "WIN_NAME",
        "NUMBER_OFFERS",
        "B_CONTRACTOR_SME",
    ]

    data_path = Path(__file__).parent / "data" / "ted_clean.parquet"
    remote_parquet_url = os.getenv("TED_PARQUET_URL", "").strip()

    if data_path.exists():
        df = pd.read_parquet(data_path, columns=needed_cols)
    elif remote_parquet_url:
        df = pd.read_parquet(remote_parquet_url, columns=needed_cols)
    else:
        st.error(
            "Data file not found. Add data/ted_clean.parquet to the repo or set TED_PARQUET_URL in Streamlit app settings."
        )
        st.stop()

    df["DT_AWARD"] = pd.to_datetime(df["DT_AWARD"], errors="coerce")
    df = df[df["DT_AWARD"].dt.year.between(2018, 2023)]
    df["YEAR"] = df["DT_AWARD"].dt.year.astype(int)

    # Reduce memory footprint for repeated values used in filters/plots.
    for col in [
        "TYPE_OF_CONTRACT",
        "ISO_COUNTRY_CODE",
        "WIN_COUNTRY_CODE",
        "CAE_TYPE",
        "MAIN_ACTIVITY",
        "B_CONTRACTOR_SME",
    ]:
        df[col] = df[col].astype("category")

    df["AWARD_VALUE_EURO"] = pd.to_numeric(df["AWARD_VALUE_EURO"], errors="coerce")
    df["NUMBER_OFFERS"] = pd.to_numeric(df["NUMBER_OFFERS"], errors="coerce")

    df["CONTRACT_TYPE_LABEL"] = (
        df["TYPE_OF_CONTRACT"].astype("string").map(CONTRACT_TYPE_LABELS).fillna("Other")
    )
    df["CPV_STR"] = df["CPV"].astype(str).str.zfill(8)
    df["CPV_DIV"] = df["CPV_STR"].str[:2]
    df["CPV_LABEL"] = df["CPV_DIV"].map(CPV_DIVISIONS).fillna("Other")
    # Cap extreme outliers for display (keep for KPI totals but cap for charts)
    df["VALUE_CAPPED"] = df["AWARD_VALUE_EURO"].clip(upper=df["AWARD_VALUE_EURO"].quantile(0.99))
    return df


# ── Load ──────────────────────────────────────────────────────────────────────
df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.title("Filters")

years = sorted(df["YEAR"].unique())
year_range = st.sidebar.select_slider("Year", options=years, value=(min(years), max(years)))

countries = sorted(df["ISO_COUNTRY_CODE"].dropna().unique())
selected_countries = st.sidebar.multiselect("Buyer Country", countries, default=[])

contract_types = sorted(df["CONTRACT_TYPE_LABEL"].unique())
selected_types = st.sidebar.multiselect("Contract Type", contract_types, default=[])

cpv_labels = sorted(df["CPV_LABEL"].unique())
selected_cpv = st.sidebar.multiselect("Procurement Category (CPV)", cpv_labels, default=[])

# ── Apply filters ─────────────────────────────────────────────────────────────
mask = df["YEAR"].between(*year_range)
if selected_countries:
    mask &= df["ISO_COUNTRY_CODE"].isin(selected_countries)
if selected_types:
    mask &= df["CONTRACT_TYPE_LABEL"].isin(selected_types)
if selected_cpv:
    mask &= df["CPV_LABEL"].isin(selected_cpv)

filtered = df[mask]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("EU Public Procurement Benchmark Dashboard")
st.caption("Source: TED (Tenders Electronic Daily) — Contract Award Notices 2018–2023")
st.markdown(
    "This dashboard benchmarks EU public procurement activity across countries, contract types, and categories to highlight spending patterns, competition levels, and supplier outcomes."
)

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_value = filtered["AWARD_VALUE_EURO"].sum()
total_contracts = len(filtered)
avg_value = filtered["AWARD_VALUE_EURO"].median()
n_countries = filtered["ISO_COUNTRY_CODE"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Contracts", f"{total_contracts:,}")
k2.metric("Total Value (EUR)", f"€{total_value / 1e9:.1f}B")
k3.metric("Median Contract Value", f"€{avg_value:,.0f}")
k4.metric("Buyer Countries", n_countries)

st.divider()

# ── Row 1: Spending over time + Contract type split ───────────────────────────
c1, c2 = st.columns([2, 1])

with c1:
    trend = (
        filtered.groupby("YEAR")["AWARD_VALUE_EURO"]
        .sum()
        .reset_index()
        .rename(columns={"AWARD_VALUE_EURO": "Total Value (EUR)"})
    )
    trend["Total Value (EUR B)"] = trend["Total Value (EUR)"] / 1e9
    fig = px.bar(
        trend, x="YEAR", y="Total Value (EUR B)",
        title="Total Contract Value by Year (EUR Billion)",
        labels={"Total Value (EUR B)": "EUR Billion", "YEAR": "Year"},
        color_discrete_sequence=["#1f77b4"],
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    type_split = filtered.groupby("CONTRACT_TYPE_LABEL")["AWARD_VALUE_EURO"].sum().reset_index()
    fig2 = px.pie(
        type_split, values="AWARD_VALUE_EURO", names="CONTRACT_TYPE_LABEL",
        title="Spend by Contract Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Top countries + Top CPV categories ────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    top_countries = (
        filtered.groupby("ISO_COUNTRY_CODE")["AWARD_VALUE_EURO"]
        .sum()
        .nlargest(15)
        .reset_index()
    )
    top_countries["EUR Billion"] = top_countries["AWARD_VALUE_EURO"] / 1e9
    fig3 = px.bar(
        top_countries.sort_values("EUR Billion"),
        x="EUR Billion", y="ISO_COUNTRY_CODE",
        orientation="h",
        title="Top 15 Buyer Countries by Spend",
        labels={"ISO_COUNTRY_CODE": "Country"},
        color_discrete_sequence=["#2ca02c"],
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    top_cpv = (
        filtered.groupby("CPV_LABEL")["AWARD_VALUE_EURO"]
        .sum()
        .nlargest(15)
        .reset_index()
    )
    top_cpv["EUR Billion"] = top_cpv["AWARD_VALUE_EURO"] / 1e9
    fig4 = px.bar(
        top_cpv.sort_values("EUR Billion"),
        x="EUR Billion", y="CPV_LABEL",
        orientation="h",
        title="Top 15 Procurement Categories (CPV)",
        labels={"CPV_LABEL": "Category"},
        color_discrete_sequence=["#ff7f0e"],
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Competition analysis ───────────────────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    comp = filtered.dropna(subset=["NUMBER_OFFERS"])
    comp = comp[comp["NUMBER_OFFERS"].between(1, 50)]
    avg_offers = comp.groupby("YEAR")["NUMBER_OFFERS"].mean().reset_index()
    fig5 = px.line(
        avg_offers, x="YEAR", y="NUMBER_OFFERS",
        title="Avg. Number of Bidders per Contract (by Year)",
        labels={"NUMBER_OFFERS": "Avg. Bids", "YEAR": "Year"},
        markers=True,
        color_discrete_sequence=["#d62728"],
    )
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    sme = filtered["B_CONTRACTOR_SME"].value_counts().reset_index()
    sme.columns = ["SME", "Count"]
    sme["SME"] = sme["SME"].map({"Y": "SME Winner", "N": "Large Firm Winner"}).fillna("Unknown")
    fig6 = px.pie(
        sme, values="Count", names="SME",
        title="SME vs Large Firm Contract Wins",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig6.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig6, use_container_width=True)

# ── Raw data preview ──────────────────────────────────────────────────────────
with st.expander("Preview filtered data"):
    st.dataframe(
        filtered[["DT_AWARD", "YEAR", "ISO_COUNTRY_CODE", "WIN_COUNTRY_CODE",
                   "CONTRACT_TYPE_LABEL", "CPV_LABEL", "AWARD_VALUE_EURO",
                   "WIN_NAME", "TITLE", "NUMBER_OFFERS"]].head(500),
        use_container_width=True,
    )