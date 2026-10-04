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
layout_mode, view_mode = render_header(show_layout_control=True)


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



def render_chart(
    chart_number: int,
    controls_container,
    chart_container,
) -> None:

    controls = controls_container


    # ---------------------------------------------------------
    # Occupation browser
    # ---------------------------------------------------------

    occupations = (
        df.loc[
            df["is_occupation_code"].fillna(False),
            [
                "occupation_code",
                "occupation_name",
                "occupation_level",
            ],
        ]
        .dropna()
        .drop_duplicates()
        .copy()
    )

    occupations["occupation_code"] = (
        occupations["occupation_code"].astype(str)
    )

    GERMANY_CODE = "DE"
    GERMANY_LABEL = "Germany — All occupations"


    # ---------------------------------------------------------
    # Occupation state
    # ---------------------------------------------------------

    selected_code_key = f"selected_occupation_code_{chart_number}"

    if selected_code_key not in st.session_state:
        st.session_state[selected_code_key] = GERMANY_CODE


    # ---------------------------------------------------------
    # Helper functions
    # ---------------------------------------------------------

    def get_occupation_row(code):
        if code == GERMANY_CODE:
            return None

        rows = occupations.loc[
            occupations["occupation_code"] == str(code)
        ]

        if rows.empty:
            return None

        return rows.iloc[0]


    def get_children(parent_code):
        """
        Return only the direct children of the current node.

        Germany -> level 1
        1       -> level 2 codes starting with 1
        11      -> level 3 codes starting with 11
        etc.
        """

        if parent_code is None:
            children = occupations.loc[
                occupations["occupation_level"] == 1
            ].copy()

        else:
            parent_row = get_occupation_row(parent_code)

            if parent_row is None:
                return occupations.iloc[0:0].copy()

            parent_level = int(parent_row["occupation_level"])
            child_level = parent_level + 1

            children = occupations.loc[
                (occupations["occupation_level"] == child_level)
                & (
                    occupations["occupation_code"]
                    .str.startswith(str(parent_code))
                )
            ].copy()

        return children.sort_values("occupation_code")


    def get_parent_code(code):
        row = get_occupation_row(code)

        if row is None:
            return None

        code = str(code)
        level = int(row["occupation_level"])

        if level <= 1:
            return None

        possible_parents = occupations.loc[
            occupations["occupation_level"] == level - 1
        ].copy()

        possible_parents = possible_parents.loc[
            possible_parents["occupation_code"]
            .astype(str)
            .apply(
                lambda parent_code:
                code.startswith(parent_code)
            )
        ]

        if possible_parents.empty:
            return None

        return (
            possible_parents
            .assign(
                code_length=(
                    possible_parents["occupation_code"]
                    .astype(str)
                    .str.len()
                )
            )
            .sort_values(
                "code_length",
                ascending=False,
            )
            .iloc[0]["occupation_code"]
        )


    # ---------------------------------------------------------
    # Occupation
    # ---------------------------------------------------------

    controls.markdown(
        '<p style="font-size: 14px; font-weight: 600; '
        'margin: 0 0 8px 0;">Occupation</p>',
        unsafe_allow_html=True,
    )


    selected_code = st.session_state[selected_code_key]

    if selected_code != GERMANY_CODE:
        if controls.button(
            "‹ Back",
            key=f"occupation_back_{chart_number}",
            type="tertiary",
        ):
            parent_code = get_parent_code(selected_code)

            if parent_code is None:
                st.session_state[selected_code_key] = GERMANY_CODE
            else:
                st.session_state[selected_code_key] = str(parent_code)

            st.rerun()

    # ---------------------------------------------------------
    # Global search
    # ---------------------------------------------------------

    search_codes = (
        occupations["occupation_code"]
        .astype(str)
        .tolist()
    )

    search_names = dict(
        zip(
            occupations["occupation_code"].astype(str),
            occupations["occupation_name"].astype(str),
        )
    )

    search_options = [None, GERMANY_CODE] + search_codes

    search_key = (
        f"occupation_search_"
        f"{chart_number}_{st.session_state[selected_code_key]}"
    )

    searched_code = controls.selectbox(
        "Search occupations",
        search_options,
        index=0,
        format_func=lambda code: (
            "🔎︎ Search all occupations..."
            if code is None
            else GERMANY_LABEL
            if code == GERMANY_CODE
            else search_names[code]
        ),
        key=search_key,
        label_visibility="collapsed",
    )

    if (
        searched_code is not None
        and str(searched_code)
        != str(st.session_state[selected_code_key])
    ):
        st.session_state[selected_code_key] = str(searched_code)
        st.rerun()


    # ---------------------------------------------------------
    # Browse by category
    # ---------------------------------------------------------

    selected_code = str(
        st.session_state[selected_code_key]
    )

    if selected_code == GERMANY_CODE:
        browse_parent = None
    else:
        browse_parent = selected_code

    children = get_children(browse_parent)

    if not children.empty:

        child_codes = (
            children["occupation_code"]
            .astype(str)
            .tolist()
        )

        child_names = dict(
            zip(
                children["occupation_code"].astype(str),
                children["occupation_name"].astype(str),
            )
        )

        child_options = [None] + child_codes

        browse_key = (
            f"occupation_browse_"
            f"{chart_number}_{selected_code}"
        )

        selected_child = controls.selectbox(
            "Browse by category",
            child_options,
            index=0,
            format_func=lambda code: (
                "🔎︎ Browse by category"
                if code is None
                else child_names[code]
            ),
            key=browse_key,
            label_visibility="collapsed",
        )

        if selected_child is not None:
            st.session_state[selected_code_key] = str(
                selected_child
            )

            st.rerun()


    # ---------------------------------------------------------
    # Resolve selected occupation for the existing chart code
    # ---------------------------------------------------------

    selected_code = st.session_state[selected_code_key]

    if selected_code == GERMANY_CODE:

        selected_name = "Germany"
        selected_occupation_level = 0

        occupation_df = df.loc[
            (df["occupation_level"] == 0)
            & (
                df["occupation_code"].astype(str)
                == GERMANY_CODE
            )
        ].copy()

    else:

        selected_row = get_occupation_row(selected_code)

        selected_name = selected_row["occupation_name"]
        selected_occupation_level = int(
            selected_row["occupation_level"]
        )

        occupation_df = df.loc[
            df["is_occupation_code"].fillna(False)
            & (
                df["occupation_code"].astype(str)
                == str(selected_code)
            )
            & (
                df["occupation_name"].astype(str)
                == str(selected_name)
            )
            & (
                df["occupation_level"]
                == selected_occupation_level
            )
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

    qualification_col = controls


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

    indicator_controls = [
        ("Vacancies", "Registered vacancies", "🔴"),
        ("Employed", "Employed people", "🔵"),
        ("Unemployed", "Unemployed people", "🟡"),
        ("Job seekers", "Job seekers", "🟢"),
    ]

    controls.markdown(
        '<p style="font-size: 14px; font-weight: 600; margin: 0 0 8px 0;">Indicators</p>',
        unsafe_allow_html=True,
    )



    selected_indicators = []

    for label, indicator, dot in indicator_controls:
        state_key = f"indicator_state_{chart_number}_{label}"

        if state_key not in st.session_state:
            st.session_state[state_key] = label != "Job seekers"

        is_selected = st.session_state[state_key]

        button_label = (
            f"{dot}  {label}"
            if is_selected
            else f"  ◯   {label}"
        )

        if controls.button(
            button_label,
            key=f"indicator_button_{chart_number}_{label}",
            use_container_width=True,
        ):
            st.session_state[state_key] = not is_selected
            st.rerun()

        if is_selected:
            selected_indicators.append(indicator)


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
        "Germany — All occupations"
        if selected_occupation_level == 0
        else selected_name
    )

    chart_card = chart_container


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
                    title=None,
                ),
                y=alt.Y(
                    "value:Q",
                    title=y_axis_title,
                ),
                color=alt.Color(
                    "indicator:N",
                    scale=color_scale,
                    legend=None,
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
                height=460,
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


workspace_left, workspace_right = st.columns(
    [0.8, 3.2],
    gap="medium",
)

with workspace_left:
    controls_1 = st.container(border=True)

with workspace_right:
    chart_1 = st.container(border=True)

render_chart(
    chart_number=1,
    controls_container=controls_1,
    chart_container=chart_1,
)

# button_col_1, button_col_2 = st.columns([1, 1])

# with button_col_1:
#     if st.button("➕ Add chart"):
#         st.session_state.chart_count += 1
#         st.rerun()

# with button_col_2:
#     if st.session_state.chart_count > 1:
#         if st.button("✕ Remove chart"):
#             st.session_state.chart_count -= 1
#             st.rerun()

