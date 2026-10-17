from pathlib import Path

import streamlit as st
from lme_brand import lme_compass_button_style, lme_home_button_style


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

        /* Stack paired chart panels only when the viewport is genuinely narrow.
           Do not use height, landscape orientation or touch capability here:
           those conditions can mistakenly stack charts on 15-inch laptops. */
        @media (max-width: 1050px) {
            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b) {
                flex-direction: column !important;
                gap: 0.75rem !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="stColumn"] {
                flex: 0 0 auto !important;
                width: 100% !important;
                max-width: 100% !important;
                min-width: 0 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="stColumn"]:nth-child(3) {
                order: 4 !important;
            }

            div[data-testid="stHorizontalBlock"]:has(.st-key-chart_b)
            > div[data-testid="stColumn"]:nth-child(4) {
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


def _render_information_header():
    """Retain the current informational-page navigation until About is redesigned."""
    header_logo, header_nav = st.columns([1, 4], vertical_alignment="center")

    with header_logo:
        st.markdown(lme_compass_button_style(), unsafe_allow_html=True)
        if st.button("LME", key="lme_home_button", type="tertiary", help="Open Welcome"):
            st.session_state["lme_screen"] = "welcome"
            st.switch_page("app.py")

    with header_nav:
        _, nav_section_switch, nav_about = st.columns(
            [5, 2.2, 1], vertical_alignment="center"
        )

    with nav_section_switch:
        if st.button("Dashboard", key="nav_section_switch", width="stretch"):
            st.switch_page("app.py")

    # Historical informational-page button is retained here only; it is not
    # displayed on the Explorer workspace.
    with nav_about:
        st.button("About", key="nav_about", width="stretch")

    return None, None


def _explorer_header_style() -> str:
    """Compact, scoped Explorer toolbar: Home + languages / view + layout.

    Global values are intentionally unchanged: the charts still expect
    global_view_mode = Absolute|Indexed and chart_layout = Single|Compare|Combined.
    """
    return """
    <style>
      /* Explorer only: reduce space above the toolbar on laptop/desktop.
         Welcome and narrow mobile layouts keep their existing spacing. */
      @media (min-width: 1051px) {
          .stMainBlockContainer:has(.st-key-lme_explorer_toolbar) {
              padding-top: 0.45rem !important;
          }
      }
      .st-key-lme_explorer_toolbar {
          padding-bottom: 0.65rem;
          margin-bottom: 0.7rem;
      }
      .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] {
          align-items: center !important;
      }
      .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
          min-width: 0 !important;
      }
      .st-key-lme_explorer_toolbar button {
          white-space: nowrap;
      }

      /* Languages sit next to Home. Only English is available for now. */
      .st-key-lme_explorer_toolbar .lme-language-strip {
          display: flex;
          align-items: center;
          justify-content: flex-start;
          gap: 0.35rem;
          min-height: 40px;
          white-space: nowrap;
          font-size: 0.88rem;
          line-height: 1.2;
      }
      .st-key-lme_explorer_toolbar .lme-language-active {
          font-weight: 700;
          color: var(--lme-text);
      }
      .st-key-lme_explorer_toolbar .lme-language-planned {
          color: var(--lme-text-secondary);
          opacity: 0.72;
      }
      .st-key-lme_explorer_toolbar .lme-language-divider {
          color: #c1c6cd;
          font-weight: 400;
      }

      /* Two robust icon-only native buttons for data view. The SVG sits on
         the button itself, so it is independent of Streamlit's text DOM. */
      .st-key-lme_explorer_toolbar .st-key-lme_view_absolute button,
      .st-key-lme_explorer_toolbar .st-key-lme_view_indexed button {
          height: 38px !important;
          min-height: 38px !important;
          min-width: 42px !important;
          padding: 0 !important;
          border: 0 !important;
          border-radius: 7px !important;
          box-shadow: none !important;
          background-color: transparent !important;
          background-repeat: no-repeat !important;
          background-position: center !important;
          background-size: 21px 21px !important;
          /* Keep the button's accessible text while removing it visually. */
          font-size: 0 !important;
          line-height: 0 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_absolute button *,
      .st-key-lme_explorer_toolbar .st-key-lme_view_indexed button * {
          font-size: 0 !important;
          line-height: 0 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_absolute button {
          background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxNzE3MTciIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNiAyMHYtN00xMiAyMFY1TTE4IDIwdi0xMSIvPjwvc3ZnPg==") !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_indexed button {
          background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxNzE3MTciIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48bGluZSB4MT0iMTkiIHkxPSI1IiB4Mj0iNSIgeTI9IjE5Ii8+PGNpcmNsZSBjeD0iNi41IiBjeT0iNi41IiByPSIyLjI1Ii8+PGNpcmNsZSBjeD0iMTcuNSIgY3k9IjE3LjUiIHI9IjIuMjUiLz48L3N2Zz4=") !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_absolute button:hover,
      .st-key-lme_explorer_toolbar .st-key-lme_view_indexed button:hover {
          background-color: #f0f1f3 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_buttons div[data-testid="stHorizontalBlock"] {
          align-items: center !important;
          gap: 0.15rem !important;
      }
      /* Chart layout keeps its existing textual segmented control. */
      .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-variant="segmented_control"] {
          border: 0 !important;
          box-shadow: none !important;
          background: transparent !important;
          color: var(--lme-text-secondary) !important;
          border-radius: 7px !important;
          transition: background-color 120ms ease, color 120ms ease;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-selected="true"] {
          background: #e9ebef !important;
          color: var(--lme-text) !important;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout button:hover {
          background: #f0f1f3 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout div[role="group"] {
          gap: 0 !important;
          border: 0 !important;
          box-shadow: none !important;
          background: transparent !important;
      }

      /* One | Two | Overlay — textual alternatives, no chart icon.
         A small divider separates this group from the icon-only view control. */
      .st-key-lme_explorer_toolbar .lme-toolbar-divider {
          display: block;
          width: 1px;
          height: 23px;
          background: var(--lme-border-strong);
          margin: 0 auto;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-variant="segmented_control"] {
          min-height: 38px !important;
          font-size: 0.87rem !important;
          padding: 0.34rem 0.55rem !important;
          font-weight: 500 !important;
          position: relative;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-variant="segmented_control"][data-selected="true"] {
          font-weight: 700 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-variant="segmented_control"]:not(:last-of-type)::after {
          content: "|";
          position: absolute;
          right: -2px;
          color: #c1c6cd;
          font-weight: 400;
      }

      /* Narrow viewports: navigation/language on row 1, analysis controls on row 2. */
      @media (max-width: 1050px) {
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] {
              display: grid !important;
              grid-template-columns: repeat(12, minmax(0, 1fr)) !important;
              gap: 0.45rem !important;
              align-items: center !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
              min-width: 0 !important;
              width: 100% !important;
              max-width: none !important;
          }
          /* 1 Home; 2 languages; 3 desktop spacer; 4 view; 5 divider; 6 layout. */
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
              grid-column: span 2;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
              grid-column: span 10;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3),
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(5) {
              display: none !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) {
              grid-column: span 4;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(6) {
              grid-column: span 8;
          }
          .st-key-lme_explorer_toolbar .lme-language-strip {
              font-size: 0.84rem;
              gap: 0.3rem;
          }
          .st-key-lme_explorer_toolbar .st-key-chart_layout button[data-variant="segmented_control"] {
              font-size: 0.83rem !important;
              padding: 0.32rem 0.42rem !important;
          }
          /* Do not turn the two icon buttons into a twelve-column grid. */
          .st-key-lme_explorer_toolbar .st-key-lme_view_buttons div[data-testid="stHorizontalBlock"] {
              display: flex !important;
              gap: 0.2rem !important;
          }
          .st-key-lme_explorer_toolbar .st-key-lme_view_buttons div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
              flex: 1 1 0 !important;
              width: 50% !important;
              min-width: 0 !important;
              max-width: 50% !important;
          }
          .st-key-lme_explorer_toolbar {
              padding-bottom: 0.5rem;
              margin-bottom: 0.55rem;
          }
      }
    </style>
    """


def _render_explorer_header():
    """Two logical groups: navigation/language left; data modes/layout right."""
    st.markdown(_explorer_header_style(), unsafe_allow_html=True)
    st.markdown(lme_home_button_style(), unsafe_allow_html=True)

    # Preserve values consumed by the existing charts. Don't rename these keys.
    if st.session_state.get("global_view_mode") not in ("Absolute", "Indexed"):
        st.session_state.global_view_mode = "Absolute"
    if st.session_state.get("chart_layout") not in ("Single", "Compare", "Combined"):
        st.session_state.chart_layout = "Compare"

    layout_labels = {
        "Single": "One",
        "Compare": "Two",
        "Combined": "Overlay",
    }

    # Current data view is indicated by a quiet gray background.
    selected_view_button = (
        "lme_view_absolute"
        if st.session_state.global_view_mode == "Absolute"
        else "lme_view_indexed"
    )
    st.markdown(
        f'<style>.st-key-lme_explorer_toolbar .st-key-{selected_view_button} '
        'button { background-color: #e9ebef !important; }</style>',
        unsafe_allow_html=True,
    )

    with st.container(key="lme_explorer_toolbar"):
        home_col, language_col, spacer_col, view_col, divider_col, layout_col = st.columns(
            [0.55, 1.30, 7.25, 1.20, 0.18, 2.45],
            gap="small",
            vertical_alignment="center",
        )

        with home_col:
            if st.button(
                "Home",
                key="lme_explorer_home",
                type="tertiary",
                help="Back to Welcome",
                width="content",
            ):
                st.session_state["lme_screen"] = "welcome"
                st.switch_page("app.py")

        with language_col:
            st.markdown(
                """<div class="lme-language-strip" role="group"
                     aria-label="Languages: English available; German and Ukrainian planned">
                     <span class="lme-language-active" aria-current="true"
                           title="English — current language">En</span>
                     <span class="lme-language-divider" aria-hidden="true">|</span>
                     <span class="lme-language-planned" title="Deutsch — coming later">De</span>
                     <span class="lme-language-divider" aria-hidden="true">|</span>
                     <span class="lme-language-planned" title="Українська — coming later">Ua</span>
                   </div>""",
                unsafe_allow_html=True,
            )

        with view_col:
            # Use separate stable button keys rather than injecting icons into
            # Streamlit's internal segmented-control markup.
            with st.container(key="lme_view_buttons"):
                absolute_col, indexed_col = st.columns(2, gap="small")
                with absolute_col:
                    if st.button(
                        "Absolute values",
                        key="lme_view_absolute",
                        help="Absolute values",
                        type="tertiary",
                        width="stretch",
                    ):
                        st.session_state.global_view_mode = "Absolute"
                        st.rerun()
                with indexed_col:
                    if st.button(
                        "Indexed (start = 100)",
                        key="lme_view_indexed",
                        help="Indexed (start = 100), not percentages",
                        type="tertiary",
                        width="stretch",
                    ):
                        st.session_state.global_view_mode = "Indexed"
                        st.rerun()

        with divider_col:
            st.markdown(
                '<span class="lme-toolbar-divider" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )

        with layout_col:
            st.segmented_control(
                "Chart layout",
                options=list(layout_labels),
                format_func=lambda mode: layout_labels[mode],
                key="chart_layout",
                label_visibility="collapsed",
                width="stretch",
            )

    return st.session_state.chart_layout, st.session_state.global_view_mode


def render_header(show_layout_control: bool = False):
    """Return chart layout and view mode; retain historical info-page support."""
    if show_layout_control:
        return _render_explorer_header()
    return _render_information_header()
