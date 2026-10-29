from pathlib import Path

import streamlit as st
from lme_brand import lme_compass_button_style, lme_home_button_style
from lme_i18n import tr


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
    language = st.session_state.get("lme_language", "En")
    header_logo, header_nav = st.columns([1, 4], vertical_alignment="center")

    with header_logo:
        st.markdown(lme_compass_button_style(), unsafe_allow_html=True)
        if st.button("LME", key="lme_home_button", type="tertiary", help=tr("Open Welcome", language)):
            st.session_state["lme_screen"] = "welcome"
            st.switch_page("app.py")

    with header_nav:
        _, nav_section_switch, nav_about = st.columns(
            [5, 2.2, 1], vertical_alignment="center"
        )

    with nav_section_switch:
        if st.button(tr("Dashboard", language), key="nav_section_switch", width="stretch"):
            st.switch_page("app.py")

    # Historical informational-page button is retained here only; it is not
    # displayed on the Explorer workspace.
    with nav_about:
        st.button(tr("About", language), key="nav_about", width="stretch")

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

      /* EN/DE occupation labels: compact native Streamlit selector; UA
         stays a visibly inactive placeholder until localization is ready. */
      .st-key-lme_explorer_toolbar .st-key-lme_language {
          min-width: 0 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language
      [data-testid="stSegmentedControl"] {
          width: max-content !important;
          max-width: 100% !important;
          min-height: 38px !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language [role="group"] {
          display: flex !important;
          align-items: center !important;
          gap: 0 !important;
          background: transparent !important;
          border: 0 !important;
          box-shadow: none !important;
          white-space: nowrap !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language
      button[data-variant="segmented_control"] {
          min-height: 36px !important;
          min-width: 28px !important;
          padding: 0.28rem 0.32rem !important;
          background: transparent !important;
          color: var(--lme-text-secondary) !important;
          border: 0 !important;
          box-shadow: none !important;
          border-radius: 5px !important;
          font-size: 0.85rem !important;
          font-weight: 500 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language
      button[data-variant="segmented_control"][data-selected="true"] {
          background: #e9ebef !important;
          color: var(--lme-text) !important;
          font-weight: 700 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language
      button[data-variant="segmented_control"]:hover {
          background: #f0f1f3 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_language [role="group"]::after {
          content: "|  Ua";
          display: inline-block;
          margin-left: 0.28rem;
          color: var(--lme-text-secondary);
          opacity: 0.65;
          font-size: 0.84rem;
          white-space: pre;
      }

      /* One compact control for chart scale. Its label is the ACTIVE mode.
         Keep the trigger within the existing toolbar column on every screen. */
      .st-key-lme_explorer_toolbar .st-key-lme_view_mode [data-testid="stPopover"] button {
          height: 38px !important;
          min-height: 38px !important;
          width: 100% !important;
          min-width: 0 !important;
          padding: 0 0.45rem !important;
          border: 0 !important;
          border-radius: 7px !important;
          box-shadow: none !important;
          background: #e9ebef !important;
          color: var(--lme-text) !important;
          font-size: 0.86rem !important;
          font-weight: 700 !important;
          white-space: nowrap !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_mode [data-testid="stPopover"] button:hover {
          background: #dee2e8 !important;
      }
      .st-key-lme_explorer_toolbar .st-key-lme_view_mode [data-testid="stPopover"] button:focus-visible {
          outline: 2px solid #8093aa !important;
          outline-offset: 2px !important;
      }
      /* Abs/Idx popup: visually belongs to the LIGHT toolbar, rather than
         inheriting the Explorer's dark occupation-dropdown styling.
         :has(marker) scopes the rule to this popover even though Streamlit
         renders its body in a portal outside the toolbar. */
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker) {
          background: #e3e6eb !important;
          color: #171717 !important;
          border: 1px solid #cbd2db !important;
          border-radius: 12px !important;
          box-shadow: 0 8px 24px rgba(25, 35, 48, .13) !important;
          padding: 0.35rem !important;
          width: min(300px, calc(100vw - 24px)) !important;
          max-width: calc(100vw - 24px) !important;
      }
      /* Desktop can fit the two short options in a narrower popup. */
      @media (min-width: 769px) {
          body:has(.st-key-lme_explorer_toolbar)
          [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker) {
              width: 280px !important;
          }
      }
      /* Streamlit renders this popup in a BaseWeb portal. The outer portal
         and the nested divs must also be reset: app.py styles occupation
         popovers dark and would otherwise create a black surround. */
      body:has(.st-key-lme_explorer_toolbar)
      [data-baseweb="popover"]:has(.lme-mode-popover-marker) {
          background: #e3e6eb !important;
          border-radius: 12px !important;
      }
      /* The occupation dropdown has global dark BaseWeb portal rules in
         app.py. Reset the *nested portal wrappers*, without touching the
         light body itself. Otherwise dark blocks can remain on mobile. */
      body:has(.st-key-lme_explorer_toolbar)
      [data-baseweb="popover"]:has(.lme-mode-popover-marker)
      :is(div, ul, li, p, span, label):not([data-testid="stPopoverBody"]) {
          background-color: transparent !important;
          color: #171717 !important;
      }
      /* No empty marker row or Streamlit's default generous vertical gap. */
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [data-testid="stElementContainer"]:has(.lme-mode-popover-marker) {
          display: none !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [data-testid="stVerticalBlock"] {
          gap: 0.25rem !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      :is(div, ul, li, p, span, label) {
          color: #171717 !important;
          background-color: transparent !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      :is([data-testid="stVerticalBlock"], [data-testid="stElementContainer"],
          [data-testid="stButton"], [data-testid="stMarkdownContainer"]) {
          background: transparent !important;
          border: 0 !important;
          box-shadow: none !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [class*="st-key-lme_mode_select_"] button {
          background: transparent !important;
          color: #171717 !important;
          border: 1px solid transparent !important;
          box-shadow: none !important;
          border-radius: 8px !important;
          padding: 0.32rem 0.55rem !important;
          min-height: 34px !important;
          font-weight: 500 !important;
          font-size: 0.85rem !important;
          justify-content: flex-start !important;
          text-align: left !important;
          white-space: normal !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [class*="st-key-lme_mode_select_"] button :is(p, span) {
          color: #171717 !important;
          background: transparent !important;
          font-family: inherit !important;
          font-size: inherit !important;
          font-weight: inherit !important;
          white-space: normal !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [class*="st-key-lme_mode_select_"] button:hover {
          background: #d4dbe5 !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [class*="st-key-lme_mode_select_"] button:focus-visible {
          outline: 2px solid #8093aa !important;
          outline-offset: 1px !important;
      }
      body:has(.st-key-lme_explorer_toolbar)
      [data-testid="stPopoverBody"]:has(.lme-mode-popover-marker)
      [class*="st-key-lme_mode_select_"] button[data-testid="stBaseButton-primary"] {
          background: #d4dbe5 !important;
          font-weight: 700 !important;
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

       /* Small persistent entry to the separate How it works guide. */
       .st-key-lme_explorer_toolbar .st-key-lme_explorer_help button {
           height: 38px !important;
           min-height: 38px !important;
           padding: 0 .25rem !important;
           border: 0 !important;
           box-shadow: none !important;
           background: transparent !important;
           font-size: 1.1rem !important;
           font-weight: 700 !important;
           color: var(--lme-text-secondary) !important;
       }
       .st-key-lme_explorer_toolbar .st-key-lme_explorer_help button:hover {
           background: #e9ebef !important;
           color: var(--lme-text) !important;
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
          /* 1 Home; 2 languages; 3 spacer; 4 view; 5 divider; 6 layout; 7 Help. */
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) {
              grid-column: span 2;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
              grid-column: span 8;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(7) {
              grid-column: 11 / 13;
              grid-row: 1;
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
          .st-key-lme_explorer_toolbar {
              padding-bottom: 0.5rem;
              margin-bottom: 0.55rem;
          }
      }

      /* V14 mobile toolbar preview: ONE line, desktop selectors untouched.
         The media condition matches app.py's phone-sized viewport detection. */
      .st-key-lme_explorer_toolbar .st-key-lme_mobile_compare {
          display: none !important;
      }
      @media (max-width: 600px) and (max-height: 1000px),
             (max-height: 600px) and (max-width: 1000px) {
          /* Five slots: Home / languages / mode / comparison / Help. */
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"] {
              grid-template-columns: 44px minmax(0, 1fr) 70px 42px 34px !important;
              gap: 0.15rem !important;
              align-items: center !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"]
          > div[data-testid="stColumn"]:nth-child(1) {
              grid-column: 1 !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"]
          > div[data-testid="stColumn"]:nth-child(2) {
              grid-column: 2 !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"]
          > div[data-testid="stColumn"]:nth-child(4) {
              grid-column: 3 !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"]
          > div[data-testid="stColumn"]:nth-child(6) {
              grid-column: 4 !important;
          }
          .st-key-lme_explorer_toolbar div[data-testid="stHorizontalBlock"]
          > div[data-testid="stColumn"]:nth-child(7) {
              grid-column: 5 !important;
              grid-row: 1 !important;
          }
          .st-key-lme_explorer_toolbar .lme-language-strip {
              gap: 0.2rem !important;
              font-size: 0.82rem !important;
          }
          /* Hide textual One/Two/Overlay only on phone-size screens. */
          .st-key-lme_explorer_toolbar .st-key-chart_layout {
              display: none !important;
          }
          .st-key-lme_explorer_toolbar .st-key-lme_mobile_compare {
              display: block !important;
          }
          .st-key-lme_explorer_toolbar .st-key-lme_mobile_compare button {
              width: 42px !important;
              min-width: 42px !important;
              height: 38px !important;
              min-height: 38px !important;
              padding: 0 !important;
              background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI4IDI4IiBmaWxsPSJub25lIiBzdHJva2U9IiMxNzE3MTciIHN0cm9rZS13aWR0aD0iMS44IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxyZWN0IHg9IjMiIHk9IjQiIHdpZHRoPSIyMiIgaGVpZ2h0PSIyMCIgcng9IjIuNSIvPjxwYXRoIGQ9Ik0zIDEwaDIyIE0xNCAxMHYxNCIvPjwvc3ZnPg==") !important;
              background-position: center !important;
              background-repeat: no-repeat !important;
              background-size: 23px 23px !important;
              border: 0 !important;
              border-radius: 7px !important;
              box-shadow: none !important;
              font-size: 0 !important;
              line-height: 0 !important;
          }
          .st-key-lme_explorer_toolbar .st-key-lme_mobile_compare button * {
              font-size: 0 !important;
              line-height: 0 !important;
          }
          .st-key-lme_explorer_toolbar .st-key-lme_mobile_compare button:hover {
              background-color: #f0f1f3 !important;
          }
          .st-key-lme_explorer_toolbar {
              padding-bottom: 0.35rem;
              margin-bottom: 0.45rem;
          }
      }
    </style>
    """


def _render_explorer_header():
    """Two logical groups: navigation/language left; data modes/layout right."""
    st.markdown(_explorer_header_style(), unsafe_allow_html=True)
    st.markdown(lme_home_button_style(), unsafe_allow_html=True)

    # EN/DE changes display strings only; selected KldB codes remain stable.
    if st.session_state.get("lme_language") not in ("En", "De"):
        st.session_state.lme_language = "En"

    # Preserve values consumed by the existing charts. Don't rename these keys.
    if st.session_state.get("global_view_mode") not in ("Absolute", "Indexed"):
        st.session_state.global_view_mode = "Absolute"
    if st.session_state.get("chart_layout") not in ("Single", "Compare", "Combined"):
        st.session_state.chart_layout = "Compare"
    # The phone UI offers only One and Overlay. If a user arrives from a
    # desktop Two session, start from One instead of showing an invisible mode.
    if (st.session_state.get("lme_last_viewport_mode") in ("portrait", "landscape")
            and st.session_state.chart_layout == "Compare"):
        st.session_state.chart_layout = "Single"

    language = st.session_state.lme_language

    def toggle_mobile_compare():
        st.session_state.chart_layout = (
            "Single" if st.session_state.chart_layout == "Combined" else "Combined"
        )

    layout_labels = {
        "Single": tr("One", language),
        "Compare": tr("Two", language),
        "Combined": tr("Overlay", language),
    }

    if st.session_state.chart_layout == "Combined":
        st.markdown(
            '<style>.st-key-lme_explorer_toolbar .st-key-lme_mobile_compare '
            'button { background-color: #e9ebef !important; }</style>',
            unsafe_allow_html=True,
        )

    with st.container(key="lme_explorer_toolbar"):
        home_col, language_col, spacer_col, view_col, divider_col, layout_col, help_col = st.columns(
            [0.55, 1.30, 6.85, 1.20, 0.18, 2.45, 0.40],
            gap="small",
            vertical_alignment="center",
        )

        with home_col:
            if st.button(
                tr("Home", language),
                key="lme_explorer_home",
                type="tertiary",
                help=tr("Back to Welcome", language),
                width="content",
            ):
                st.session_state["lme_screen"] = "welcome"
                st.switch_page("app.py")

        with language_col:
            # Existing two-character language choices become interactive.
            # Ukrainian stays a visual placeholder in the scoped toolbar CSS.
            st.segmented_control(
                "Occupation label language",  # stable invisible widget label
                options=["En", "De"],
                key="lme_language",
                selection_mode="single",
                label_visibility="collapsed",
                width="content",
            )

        with view_col:
            # This is a mode SELECTOR, not an action button. The closed label
            # always names the active mode, regardless of the chosen language.
            # Keep global_view_mode unchanged: app.py expects Absolute|Indexed.
            view_modes = {
                "Absolute": ("Abs", tr("Absolute values", language)),
                "Indexed": ("Idx", tr("Indexed (start = 100)", language)),
            }
            current_mode = st.session_state.global_view_mode
            current_short, current_description = view_modes[current_mode]
            with st.container(key="lme_view_mode"):
                with st.popover(
                    current_short,
                    help=current_description,
                    width="stretch",
                ):
                    st.html('<span class="lme-mode-popover-marker" aria-hidden="true"></span>')
                    for mode, (short_label, description) in view_modes.items():
                        is_current = mode == current_mode
                        # Four leading ASCII spaces were interpreted as an
                        # indented Markdown code block by st.button, creating
                        # the black box and monospaced text on mobile.
                        option_label = (
                            f"{'✓ ' if is_current else ''}"
                            f"{short_label} · {description}"
                        )
                        if st.button(
                            option_label,
                            key=f"lme_mode_select_{mode.lower()}",
                            type="primary" if is_current else "tertiary",
                            width="stretch",
                        ):
                            if not is_current:
                                st.session_state.global_view_mode = mode
                                st.rerun()

        with divider_col:
            st.markdown(
                '<span class="lme-toolbar-divider" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )

        with layout_col:
            # Native mobile comparison toggle. It reuses the established
            # Single/Combined values; app.py and both chart renderers are intact.
            st.button(
                tr("Exit comparison" if st.session_state.chart_layout == "Combined"
                   else "Compare occupations", language),
                key="lme_mobile_compare",
                type="tertiary",
                help=tr("Return to one chart" if st.session_state.chart_layout == "Combined"
                        else "Compare two occupations (Overlay)", language),
                on_click=toggle_mobile_compare,
                width="stretch",
            )
            st.segmented_control(
                "Chart layout",  # stable invisible widget label
                options=list(layout_labels),
                format_func=lambda mode: layout_labels[mode],
                key="chart_layout",
                label_visibility="collapsed",
                width="stretch",
            )

        with help_col:
            if st.button("?", key="lme_explorer_help", type="tertiary",
                         help=tr("How it works", language), width="stretch"):
                st.session_state["lme_help_origin"] = "explorer"
                st.session_state["lme_screen"] = "help"
                st.switch_page("app.py")

    return st.session_state.chart_layout, st.session_state.global_view_mode


def render_header(show_layout_control: bool = False):
    """Return chart layout and view mode; retain historical info-page support."""
    if show_layout_control:
        return _render_explorer_header()
    return _render_information_header()
