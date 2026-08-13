from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "german_labour_market.parquet"
LOGO_PATH = Path(__file__).parent / "assets" / "compass.png"

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the prepared labour-market dataset used by the application layer."""
    return pd.read_parquet(DATA_PATH)


st.set_page_config(page_title="Explore labour market", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #AAD2C6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.image(LOGO_PATH, width=120)

st.title("Explore the labour market")


if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

required_columns = {
    "occupation_code",
    "occupation_name",
    "qualification",
    "vacancies_current",
    "is_occupation_code",
    "report_date",
}

missing_columns = required_columns.difference(df.columns)
if missing_columns:
    st.error(
        "The processed dataset is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.stop()

# Keep only actual occupation-code rows, excluding aggregate/header rows.
occupations = (
    df.loc[df["is_occupation_code"].fillna(False), ["occupation_code", "occupation_name"]]
    .dropna()
    .drop_duplicates()
    .sort_values(["occupation_name", "occupation_code"])
)

occupations["label"] = (
    occupations["occupation_code"].astype(str)
    + " — "
    + occupations["occupation_name"].astype(str)
)

selected_label = st.selectbox(
    "Occupation",
    occupations["label"].tolist(),
    index=None,
    placeholder="Choose an occupation",
)

if selected_label is None:
    st.info("Choose an occupation to display its vacancy history.")
    st.stop()

selected_row = occupations.loc[occupations["label"] == selected_label].iloc[0]
selected_code = selected_row["occupation_code"]
selected_name = selected_row["occupation_name"]

occupation_df = df.loc[
    df["is_occupation_code"].fillna(False)
    & (df["occupation_code"] == selected_code)
    & (df["occupation_name"] == selected_name)
].copy()

qualification_options = sorted(
    occupation_df["qualification"].dropna().astype(str).unique().tolist()
)

selected_qualification = None
if len(qualification_options) > 1:
    default_index = (
        qualification_options.index("Insgesamt")
        if "Insgesamt" in qualification_options
        else 0
    )
    selected_qualification = st.selectbox(
        "Qualification level",
        qualification_options,
        index=default_index,
    )
elif len(qualification_options) == 1:
    selected_qualification = qualification_options[0]

if selected_qualification is not None:
    occupation_df = occupation_df.loc[
        occupation_df["qualification"].astype(str) == selected_qualification
    ]

chart_df = (
    occupation_df[["report_date", "vacancies_current"]]
    .dropna(subset=["report_date"])
    .sort_values("report_date")
    .set_index("report_date")
)

st.subheader(f"Registered vacancies — {selected_name}")
if selected_qualification is not None:
    st.caption(f"Qualification: {selected_qualification}")

if chart_df.empty:
    st.warning("No vacancy time series is available for this selection.")
else:
    st.line_chart(chart_df, y="vacancies_current", x_label="Date", y_label="Vacancies")
