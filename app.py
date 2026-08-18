from pathlib import Path
from ui import apply_app_style, render_header

import pandas as pd
import streamlit as st
import altair as alt

DATA_DIR = Path(__file__).parent / "data"

LABOUR_MARKET_DATA_PATH = DATA_DIR / "german_labour_market_full.parquet"
EMPLOYED_PEOPLE_DATA_PATH = DATA_DIR / "employed_people_full_kldb.parquet"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the prepared labour-market dataset used by the application layer."""
    return pd.read_parquet(LABOUR_MARKET_DATA_PATH)

@st.cache_data
def load_employed_data() -> pd.DataFrame:
    """Load the employed-persons dataset."""
    return pd.read_parquet(EMPLOYED_PEOPLE_DATA_PATH)

st.set_page_config(page_title="Explore labour market", page_icon="🧭", layout="wide")

apply_app_style()
layout_mode = render_header(show_layout_control=True)


#st.title("Explore the labour market")

if not LABOUR_MARKET_DATA_PATH.exists():
    st.error(f"Dataset not found: {LABOUR_MARKET_DATA_PATH}")
    st.stop()

try:
    df = load_data()
    employed_df = load_employed_data()

except Exception as exc:
    st.error(f"Could not load the datasets: {exc}")
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
OCCUPATION_LEVEL_LABELS = {
    0: "Entire",
    1: "Broad (1-digit)",
    2: "Groups (2-digit)",
    3: "Detailed (3-digit)",
}


def render_chart(
    chart_number: int,
    compact: bool = False,
) -> None:

    settings = st.expander(
        f"Chart {chart_number} settings",
        expanded=True,
    )

    selected_occupation_level = settings.segmented_control(
        "Occupation level",
        options=[0, 1, 2, 3],
        default=0,
        format_func=lambda level: OCCUPATION_LEVEL_LABELS[level],
        key=f"occupation_level_{chart_number}",
    )

    if selected_occupation_level == 0:
        selected_code = "DE"
        selected_name = "Germany"

    else:
        occupations = (
            df.loc[
                df["is_occupation_code"].fillna(False)
                & (df["occupation_level"] == selected_occupation_level),
                [
                    "occupation_code",
                    "occupation_name",
                ],
            ]
            .dropna()
            .drop_duplicates()
            .sort_values(["occupation_name", "occupation_code"])
        )

        occupations["label"] = (
            occupations["occupation_code"].astype(str)
            + " — "
            + occupations["occupation_name"].astype(str)
        )

        selected_label = settings.selectbox(
            "Occupation",
            occupations["label"].tolist(),
            index=None,
            placeholder="Choose an occupation",
            key=f"occupation_{chart_number}",
            width=440,
        )

        if selected_label is None:
            st.info("Choose an occupation to explore the labour market.")
            return

        selected_row = occupations.loc[
            occupations["label"] == selected_label
        ].iloc[0]

        selected_code = selected_row["occupation_code"]
        selected_name = selected_row["occupation_name"]


    if selected_occupation_level == 0:
        occupation_df = df.loc[
            (df["occupation_level"] == 0)
            & (df["occupation_code"].astype(str) == "DE")
        ].copy()

    else:
        occupation_df = df.loc[
            df["is_occupation_code"].fillna(False)
            & (df["occupation_code"] == selected_code)
            & (df["occupation_name"] == selected_name)
            & (df["occupation_level"] == selected_occupation_level)
            ].copy()

    QUALIFICATION_DISPLAY_LABELS = {
        "Insgesamt": "Overall",
        "Gesamt": "Overall",
        "Helfer": "Helfer",
        "Fachkraft": "Fachkraft",
        "Spezialist": "Spezialist",
        "Experte": "Experte",
    }

    qualification_options = sorted(
        occupation_df["qualification"].dropna().astype(str).unique().tolist()
    )


    selected_qualification = None

    if compact:
        qualification_col, view_col, _ = settings.columns(
            [1.4, 1.6, 2.22]
        )
    else:
        qualification_col, view_col, _ = settings.columns(
            [177, 180, 1000]
        )

    if len(qualification_options) > 1:
        overall_qualification = next(
            (
                qualification
                for qualification in ("Insgesamt", "Gesamt")
                if qualification in qualification_options
            ),
            qualification_options[0],
        )

        default_index = qualification_options.index(
            overall_qualification
        )

        with qualification_col:
            selected_qualification = st.selectbox(
                "Qualification level",
                qualification_options,
                index=default_index,
                format_func=lambda q: QUALIFICATION_DISPLAY_LABELS.get(q, q),
                key=f"qualification_{chart_number}",
            )

    elif len(qualification_options) == 1:
        selected_qualification = qualification_options[0]

    qualification_label = (
        QUALIFICATION_DISPLAY_LABELS.get(
            selected_qualification,
            selected_qualification,
        )
        if selected_qualification is not None
        else None
    )

    if selected_qualification is not None:
        occupation_df = occupation_df.loc[
            occupation_df["qualification"].astype(str) == selected_qualification
        ]

    # Match qualification names used by the two BA datasets.
    qualification_mapping = {
        "Insgesamt": "Gesamt",
        "Gesamt": "Gesamt",
        "Helfer": "Helfer",
        "Fachkraft": "Fachkraft",
        "Spezialist": "Spezialist",
        "Experte": "Experte",
    }

    employed_occupation_df = employed_df.loc[
        (employed_df["occupation_code"].astype(str) == str(selected_code))
        & (employed_df["occupation_level"] == selected_occupation_level)
    ].copy()

    if selected_qualification is not None:
        employed_qualification = qualification_mapping.get(
            selected_qualification
        )

        if employed_qualification is not None:
            employed_occupation_df = employed_occupation_df.loc[
                employed_occupation_df["qualification"]
                == employed_qualification
            ]
        else:
            employed_occupation_df = employed_occupation_df.iloc[0:0]

    chart_df = (
        occupation_df[["report_date", "vacancies_current"]]
        .dropna(subset=["report_date"])
        .sort_values("report_date")
        .set_index("report_date")
    )

    employed_chart_df = (
        employed_occupation_df[["report_date", "employed"]]
        .dropna(subset=["report_date"])
        .sort_values("report_date")
        .set_index("report_date")
    )

    unemployed_chart_df = (
        occupation_df[["report_date", "unemployed_current"]]
        .dropna(subset=["report_date"])
        .sort_values("report_date")
        .set_index("report_date")
    )

    job_seekers_chart_df = (
        occupation_df[["report_date", "jobseekers_current"]]
        .dropna(subset=["report_date"])
        .sort_values("report_date")
        .set_index("report_date")
    )

    INDICATORS = {
        "Registered vacancies": {
            "data": chart_df,
            "column": "vacancies_current",
            "color": "#E45756",
        },
        "Employed people": {
            "data": employed_chart_df,
            "column": "employed",
            "color": "#4C78A8",
        },
        "Unemployed people": {
            "data": unemployed_chart_df,
            "column": "unemployed_current",
            "color": "#F2CF5B",
        },
        "Job seekers": {
            "data": job_seekers_chart_df,
            "column": "jobseekers_current",
            "color": "#59A14F",
        },
    }

    indicator_labels = {
        "Vacancies": "Registered vacancies",
        "Employed": "Employed people",
        "Unemployed": "Unemployed people",
        "Job seekers": "Job seekers",
    }

    default_labels = (
        ["Vacancies"]
        if chart_number == 1
        else ["Employed"]
    )

    selected_labels = settings.segmented_control(
        "Indicators",
        options=list(indicator_labels.keys()),
        default=default_labels,
        selection_mode="multi",
        key=f"indicators_{chart_number}",
    )

    selected_indicators = [
        indicator_labels[label]
        for label in selected_labels
    ]

    with view_col:
        view_mode = st.segmented_control(
            "View",
            options=["Absolute", "Indexed"],
            default="Absolute",
            key=f"view_mode_{chart_number}",
        )

    if not selected_indicators:
        st.info("Choose at least one indicator.")
        return

    series = []

    for indicator in selected_indicators:
        config = INDICATORS[indicator]

        indicator_series = (
            config["data"][config["column"]]
            .rename(indicator)
        )

        series.append(indicator_series)

    
    combined_chart_df = pd.concat(
        series,
        axis=1,
    ).sort_index()

    plot_df = (
        combined_chart_df
        .reset_index()
        .melt(
            id_vars="report_date",
            var_name="indicator",
            value_name="value",
        )
        .dropna(subset=["value"])
    )

    if view_mode == "Indexed":
        # Find the first available date for each selected indicator.
        first_dates = (
            plot_df
            .groupby("indicator")["report_date"]
            .min()
        )

        # Use the latest starting date as the common starting period.
        common_start_date = first_dates.max()

        plot_df = plot_df.loc[
            plot_df["report_date"] >= common_start_date
        ].copy()

        # The first available value for each indicator from the
        # common starting period becomes 100.
        baseline_values = (
            plot_df
            .sort_values("report_date")
            .groupby("indicator")["value"]
            .first()
        )

        plot_df["value"] = (
            plot_df["value"]
            / plot_df["indicator"].map(baseline_values)
            * 100
        )

    y_axis_title = (
        "Index (start = 100)"
        if view_mode == "Indexed"
        else "People / vacancies"
    )

    display_name = (
    "Entire"
    if selected_occupation_level == 0
    else selected_name
    )

    chart_card = st.container(border=True)


    chart_card.markdown(
        f"""
        <div style="
            display: flex;
            align-items: baseline;
            gap: 0.7rem;
            margin-top: 0.6rem;
            margin-bottom: 0.5rem;
        ">
            <span style="
                font-size: 1.35rem;
                font-weight: 600;
            ">
                {display_name}
            </span>
            <span style="
                font-size: 1.35rem;
                opacity: 0.6;
            ">
                · {qualification_label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if combined_chart_df.empty:
        chart_card.warning(
            "No time series is available for this selection."
        )
    else:
        color_scale = alt.Scale(
            domain=[
                "Registered vacancies",
                "Employed people",
                "Unemployed people",
                "Job seekers",
            ],
            range=[
                "#E45756",
                "#4C78A8",
                "#F2CF5B",
                "#59A14F",
            ],
        )

        chart = (
            alt.Chart(plot_df)
            .mark_line()
            .encode(
                x=alt.X(
                    "report_date:T",
                    title="Date",
                ),
                y=alt.Y(
                    "value:Q",
                    title=y_axis_title,
                ),
                color=alt.Color(
                    "indicator:N",
                    scale=color_scale,
                    title="Indicator",
                ),
                tooltip=[
                    alt.Tooltip(
                        "report_date:T",
                        title="Date",
                    ),
                    alt.Tooltip(
                        "indicator:N",
                        title="Indicator",
                    ),
                    alt.Tooltip(
                        "value:Q",
                        title=(
                            "Index"
                            if view_mode == "Indexed"
                            else "Value"
                        ),
                        format=",.1f"
                        if view_mode == "Indexed"
                        else ",.0f",
                    ),
                ],
            )
            .properties(
                height=350,
            )
            .interactive()
        )

        chart_card.altair_chart(
            chart,
            use_container_width=True,
        )


# Remember whether the user added a second chart.
if "chart_count" not in st.session_state:
    st.session_state.chart_count = 1


if layout_mode == "Grid":
    chart_columns = st.columns(2)

    for chart_number in range(
        1,
        st.session_state.chart_count + 1,
    ):
        with chart_columns[(chart_number - 1) % 2]:
            render_chart(chart_number, compact=True)

else:
    for chart_number in range(
        1,
        st.session_state.chart_count + 1,
    ):
        render_chart(chart_number)

button_col_1, button_col_2 = st.columns([1, 1])

with button_col_1:
    if st.button("➕ Add chart"):
        st.session_state.chart_count += 1
        st.rerun()

with button_col_2:
    if st.session_state.chart_count > 1:
        if st.button("✕ Remove chart"):
            st.session_state.chart_count -= 1
            st.rerun()

