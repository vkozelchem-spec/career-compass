from pathlib import Path

import streamlit as st


ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "LME.png"


def apply_app_style() -> None:
    """Apply the shared visual style used across the application."""

    st.markdown(
        """
        <style>

        /* =========================================================
           LME DESIGN SYSTEM
           ========================================================= */

        :root {
            --lme-bg: #f3f4f6;
            --lme-surface: #ffffff;
            --lme-surface-soft: #f8f9fa;

            --lme-text: #171717;
            --lme-text-secondary: #667085;

            --lme-border: #e2e5e9;
            --lme-border-strong: #d5d9df;

            --lme-accent: #e30613;
            --lme-accent-soft: #fff1f2;

            --lme-radius: 14px;
            --lme-radius-small: 9px;

            --lme-shadow:
                0 1px 2px rgba(16, 24, 40, 0.03),
                0 4px 12px rgba(16, 24, 40, 0.04);
        }


        /* =========================================================
           PAGE
           ========================================================= */

        .stApp {
            background: var(--lme-bg);
        }

        /* Main Streamlit content area */
        .stMainBlockContainer {
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
        }


        /* =========================================================
           STREAMLIT SIDEBAR
           We continue to use our own layout.
           ========================================================= */

        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }

        /* =========================================================
        TYPOGRAPHY
        ========================================================= */

        .stApp {
            color: var(--lme-text);
            font-weight: 500;
        }

        /* General Streamlit text */
        .stApp p,
        .stApp span,
        .stApp label,
        .stApp button,
        .stApp input {
            font-weight: 500;
        }

        /* Widget labels */
        [data-testid="stWidgetLabel"] p {
            font-weight: 600 !important;
            color: var(--lme-text) !important;
        }

        /* Selectbox text */
        div[data-baseweb="select"] {
            font-weight: 500;
        }

        /* Buttons / navigation */
        div[data-testid="stButton"] > button {
            font-weight: 550;
        }

        h1, h2, h3 {
            color: var(--lme-text);
            font-weight: 650;
            letter-spacing: -0.02em;
        }
        
        .control-label {
            font-weight: 550;
            color: var(--lme-text);
            margin-bottom: 0.5rem;
        }


        /* =========================================================
           BUTTONS
           ========================================================= */

        div[data-testid="stButton"] > button {
            background: var(--lme-surface);
            border: 1px solid var(--lme-border);
            border-radius: var(--lme-radius-small);
            box-shadow: none;

            padding: 0.42rem 0.75rem;

            font-weight: 500;
            color: var(--lme-text);

            transition:
                background-color 160ms ease,
                border-color 160ms ease,
                transform 160ms ease;
        }

        div[data-testid="stButton"] > button:hover {
            background: var(--lme-surface-soft);
            border-color: var(--lme-border-strong);
            color: var(--lme-text);
        }

        div[data-testid="stButton"] > button:active {
            transform: translateY(1px);
        }

        div[data-testid="stButton"] > button:focus {
            box-shadow: none;
        }


        /* =========================================================
           SELECTBOX
           ========================================================= */

        div[data-baseweb="select"] > div {
            background: var(--lme-surface) !important;
            border-color: var(--lme-border) !important;
            border-radius: var(--lme-radius-small) !important;
        }

        div[data-baseweb="select"] > div:focus-within {
            border-color: #98a2b3 !important;
            box-shadow: 0 0 0 1px #98a2b3 !important;
        }


        /* =========================================================
           SEGMENTED CONTROLS
           ========================================================= */

        button[data-variant="segmented_control"] {
            transition:
                background-color 160ms ease,
                color 160ms ease,
                border-color 160ms ease;
        }

        button[data-variant="segmented_control"][data-selected="true"] {
            background: var(--lme-accent) !important;
            color: white !important;
            border-color: var(--lme-accent) !important;
        }

        /* =========================================================
        INDICATOR LEGEND
        Turn multi-select segmented controls into vertical rows.
        ========================================================= */

        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) div[role="group"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
            gap: 0.3rem !important;
        }


        /* Individual indicator rows */
        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) button[data-variant="segmented_control"] {
            width: 100% !important;
            justify-content: flex-start !important;

            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 8px !important;

            padding: 0.42rem 0.6rem !important;

            color: var(--lme-text-secondary) !important;
            font-weight: 500 !important;

            transition:
                background-color 160ms ease,
                color 160ms ease,
                opacity 160ms ease !important;
        }


        /* Vacancies dot */
        div[data-testid="stSegmentedControl"]
        button[aria-label*="Vacancies"] {
            --indicator-color: #E45756;
            --indicator-bg: rgba(228, 87, 86, 0.10);
        }


        /* Employed dot */
        div[data-testid="stSegmentedControl"]
        button[aria-label*="Employed"] {
            --indicator-color: #4C78A8;
            --indicator-bg: rgba(76, 120, 168, 0.10);
        }


        /* Unemployed dot */
        div[data-testid="stSegmentedControl"]
        button[aria-label*="Unemployed"] {
            --indicator-color: #D9A514;
            --indicator-bg: rgba(217, 165, 20, 0.11);
        }


        /* Job seekers dot */
        div[data-testid="stSegmentedControl"]
        button[aria-label*="Job seekers"] {
            --indicator-color: #59A14F;
            --indicator-bg: rgba(89, 161, 79, 0.10);
        }


        /* The dot itself inherits the series colour */
        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) button[data-variant="segmented_control"]::first-letter {
            color: var(--indicator-color);
        }


        /* Selected indicator */
        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) button[data-variant="segmented_control"][data-selected="true"] {
            background: var(--indicator-bg) !important;
            border-color: transparent !important;

            color: var(--lme-text) !important;
        }


        /* Unselected indicator */
        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) button[data-variant="segmented_control"][data-selected="false"] {
            background: transparent !important;
            color: var(--lme-text-secondary) !important;
            opacity: 0.68;
        }


        /* Hover */
        div[data-testid="stSegmentedControl"]:has(
            button[aria-label*="Vacancies"]
        ) button[data-variant="segmented_control"]:hover {
            background: var(--indicator-bg) !important;
            opacity: 1;
        }


        /* =========================================================
           EXPANDERS
           Temporary styling while old layout still exists.
           These will later become control panels.
           ========================================================= */

        [data-testid="stExpander"] {
            background: var(--lme-surface);
            border: 1px solid var(--lme-border) !important;
            border-radius: var(--lme-radius);
            box-shadow: var(--lme-shadow);

            overflow: hidden;

            /* Remove old glass effect */
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
        }


        /* =========================================================
           BORDERED CONTAINERS / CHART CARDS
           ========================================================= */

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--lme-surface);
            border: 1px solid var(--lme-border) !important;
            border-radius: var(--lme-radius);
            box-shadow: var(--lme-shadow);

            backdrop-filter: none;
            -webkit-backdrop-filter: none;
        }


        /* =========================================================
           ALTAIR / VEGA CHART AREA
           ========================================================= */

        [data-testid="stVegaLiteChart"] {
            background: var(--lme-surface-soft);
            border-radius: 10px;
            overflow: hidden;
        }


        /* =========================================================
           LINKS
           ========================================================= */

        a {
            color: var(--lme-text);
        }

        a:hover {
            color: var(--lme-accent);
        }


        /* =========================================================
           RESPONSIVE FOUNDATION
           No layout changes yet — only groundwork.
           ========================================================= */

        @media (max-width: 900px) {

            .stMainBlockContainer {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 0.75rem;
            }

        }

        /* Stack the two chart groups on phones while keeping each control
           panel directly above the chart it controls. */
        @media
            (max-width: 768px),
            (pointer: coarse) and (max-width: 1600px),
            (any-pointer: coarse) and (max-width: 1600px),
            (orientation: landscape) and (pointer: coarse),
            (orientation: landscape) and (max-height: 700px) {
            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b) {
                flex-direction: column !important;
                gap: 0.75rem !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="column"] {
                flex: 0 0 100% !important;
                width: 100% !important;
                min-width: 0 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="column"]:nth-child(3) {
                order: 4 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="column"]:nth-child(4) {
                order: 3 !important;
            }
        }
        
        /* =========================================================
        INDICATOR LEGEND — TEST
        ========================================================= */

        /* Hide only the native switch control */
        .st-key-indicator_1_Employed
        [data-testid="stCheckbox"]
        label > span,
        .st-key-indicator_1_Employed
        [data-testid="stCheckbox"]
        label > div:not([data-testid="stWidgetLabel"]) {
            display: none !important;
        }


        /* Keep the whole label clickable */
        .st-key-indicator_1_Employed
        [data-testid="stCheckbox"]
        label {
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
        }


        /* Our series marker */
        .st-key-indicator_1_Employed
        [data-testid="stCheckbox"]
        label::before {
            content: "●";
            color: #4C78A8;
            font-size: 16px;
            line-height: 1;
            margin-right: 9px;
        }


        /* Dim when switched off */
        .st-key-indicator_1_Employed
        [data-testid="stCheckbox"]
        label[data-selected="false"] {
            opacity: 0.35;
        }

        /* =========================================================
        INDICATOR CONTROLS
        ========================================================= */

        [class*="st-key-indicator_button_"] button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;

            width: 100% !important;
            min-height: 34px !important;

            padding: 0.25rem 0 !important;

            display: flex !important;
            justify-content: flex-start !important;
            text-align: left !important;

            color: var(--lme-text) !important;
        }


        /* Remove button hover decoration */
        [class*="st-key-indicator_button_"] button:hover,
        [class*="st-key-indicator_button_"] button:focus,
        [class*="st-key-indicator_button_"] button:active {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }


        /* Streamlit puts the button text inside a child element */
        [class*="st-key-indicator_button_"] button > div,
        [class*="st-key-indicator_button_"] button p {
            width: auto !important;
            text-align: left !important;
            justify-content: flex-start !important;
            margin: 0 !important;
        }

        /* ---------------------------------------------------------
        Occupation browser
        --------------------------------------------------------- */

        div[data-testid="stButton"] button[kind="secondary"]:has(
            span[data-testid="stMarkdownContainer"] p
        ) {
            transition:
                background-color 0.15s ease,
                border-color 0.15s ease;
        }

        /* Browser section labels */
        .occupation-browser-section {
            margin-top: 0.85rem;
            margin-bottom: 0.25rem;

            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;

            color: #8a9099;
        }

        /* Current occupation */
        .occupation-browser-title {
            margin: 0.45rem 0 0.7rem 0;

            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.35;

            color: #171717;
        }

        /* Selected occupation shown outside Browse */
        .occupation-current-value {
            margin: 0 0 0.15rem 0;

            font-size: 0.9rem;
            font-weight: 500;
            line-height: 1.35;

            color: #171717;
        }        

        /* =========================================================
        Occupation browser
        ========================================================= */

        /* ---------- Navigation rows ---------- */

        div[data-testid="stElementContainer"]:has(.occupation-nav-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] {
            margin: 0;
        }

        div[data-testid="stElementContainer"]:has(.occupation-nav-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button {
            width: 100%;
            min-height: 2.25rem;

            padding: 0.35rem 0.25rem;

            background: transparent;
            border: none;
            border-radius: 7px;
            box-shadow: none;

            justify-content: flex-start;

            font-weight: 500;
            text-align: left;
        }

        div[data-testid="stElementContainer"]:has(.occupation-nav-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button:hover {
            background: #f0f1f3;
            border: none;
        }

        div[data-testid="stElementContainer"]:has(.occupation-nav-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button p {
            width: 100%;
            text-align: left;
        }


        /* ---------- Back / Close ---------- */

        div[data-testid="stElementContainer"]:has(.occupation-back-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button {
            width: auto;
            min-height: auto;

            padding: 0.15rem 0;

            background: transparent;
            border: none;
            box-shadow: none;

            justify-content: flex-start;

            font-size: 0.86rem;
            font-weight: 500;
            color: #667085;
        }

        div[data-testid="stElementContainer"]:has(.occupation-back-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button:hover {
            background: transparent;
            border: none;
            color: #171717;
        }


        /* ---------- Select current category ---------- */

        div[data-testid="stElementContainer"]:has(.occupation-select-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button {
            width: 100%;
            min-height: 2.2rem;

            padding: 0.35rem 0.25rem;

            background: transparent;
            border: none;
            border-radius: 7px;
            box-shadow: none;

            justify-content: flex-start;

            font-weight: 500;
            text-align: left;
        }

        div[data-testid="stElementContainer"]:has(.occupation-select-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button:hover {
            background: #f0f1f3;
            border: none;
        }

        div[data-testid="stElementContainer"]:has(.occupation-select-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"] button p {
            width: 100%;
            text-align: left;
        }


        /* ---------- Browser headings ---------- */

        .occupation-browser-title {
            margin: 0.65rem 0 0.25rem 0;

            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.35;

            color: #171717;
        }

        .occupation-browser-section {
            margin: 0.8rem 0 0.2rem 0;

            font-size: 0.78rem;
            font-weight: 600;

            color: #667085;
        }

        .occupation-current-value {
            margin: 0 0 0.15rem 0;

            font-size: 0.9rem;
            font-weight: 500;
            line-height: 1.35;

            color: #171717;
        }

        
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(show_layout_control: bool = False):
    """Render the shared Labour Market Explorer header."""

    header_logo, header_nav = st.columns(
        [1, 4],
        vertical_alignment="center",
    )

    with header_logo:
        st.image(LOGO_PATH, width=120)

    with header_nav:
        if show_layout_control:
            (
                nav_spacer,
                nav_view,
                nav_layout,
                nav_section_switch,
                nav_about,
            ) = st.columns(
                [1.8, 1.3, 2.0, 2.2, 0.9],
                vertical_alignment="center",
            )
        else:
            nav_spacer, nav_section_switch, nav_about = st.columns(
                [5, 2.2, 1],
                vertical_alignment="center",
            )

    # ---------------------------------------------------------
    # Global data view: Absolute / Indexed
    # ---------------------------------------------------------

    if show_layout_control:
        if "global_view_mode" not in st.session_state:
            st.session_state.global_view_mode = "Absolute"

        with nav_view:
            view_label = (
                "Indexed view"
                if st.session_state.global_view_mode == "Absolute"
                else "Absolute view"
            )

            if st.button(
                view_label,
                key="nav_view",
                width="stretch",
            ):
                st.session_state.global_view_mode = (
                    "Indexed"
                    if st.session_state.global_view_mode == "Absolute"
                    else "Absolute"
                )
                st.rerun()

        view_mode = st.session_state.global_view_mode

    else:
        view_mode = None

    # ---------------------------------------------------------
    # Chart layout: Single / Compare / Combined
    # ---------------------------------------------------------

    if show_layout_control:
        if st.session_state.get("chart_layout") not in (
            "Single", "Compare", "Combined"
        ):
            st.session_state.chart_layout = "Compare"

        layout_labels = {
            "Single": "One chart",
            "Compare": "Two charts",
            "Combined": "Merged chart",
        }
        with nav_layout:
            st.selectbox(
                "Chart layout",
                options=list(layout_labels),
                format_func=lambda mode: layout_labels[mode],
                key="chart_layout",
                label_visibility="collapsed",
            )

        layout_mode = st.session_state.chart_layout
    else:
        layout_mode = None

    # ---------------------------------------------------------
    # Dashboard / Data Sources toggle
    # ---------------------------------------------------------

    with nav_section_switch:
        section_label = "Data Sources" if show_layout_control else "Dashboard"
        if st.button(
            section_label,
            key="nav_section_switch",
            width="stretch",
        ):
            target_page = (
                "pages/data_sources.py"
                if show_layout_control
                else "app.py"
            )
            st.switch_page(target_page)

    with nav_about:
        st.button(
            "About",
            key="nav_about",
            width="stretch"
        )

    return layout_mode, view_mode