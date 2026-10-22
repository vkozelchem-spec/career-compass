from pathlib import Path
import html
from ui import apply_app_style, render_header
from lme_welcome import render_welcome

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

# Browser-side preference storage. A v2 component reads and writes localStorage
# on the same browser origin. No user setting is stored on the shared server.
from lme_browser_storage import browser_skip_welcome

# Keep this component mounted on both Welcome and Explorer. Otherwise Streamlit
# could clean up its widget state while the other screen is visible.
stored_skip = browser_skip_welcome(
    write=st.session_state.get("lme_browser_write")
)

if "lme_skip_preference" not in st.session_state:
    # First browser connection: wait for localStorage before choosing a screen.
    # Do not momentarily show Welcome to people who requested to skip it.
    if stored_skip is None:
        st.caption("Loading preferences…")
        st.stop()
    st.session_state.lme_skip_preference = bool(stored_skip)

if "lme_screen" not in st.session_state:
    st.session_state.lme_screen = (
        "explorer" if st.session_state.lme_skip_preference else "welcome"
    )


def on_skip_welcome_change():
    # Streamlit removes the checkbox widget key while Explorer is displayed.
    # Preserve the domain preference separately and queue a browser write.
    skip = bool(st.session_state.lme_skip_welcome)
    st.session_state.lme_skip_preference = skip
    st.session_state.lme_browser_write = skip


def open_explorer():
    st.session_state.lme_screen = "explorer"
    st.rerun()


def open_about():
    st.switch_page("pages/data_sources.py")


if st.session_state.lme_screen == "welcome":
    render_welcome(
        on_explore=open_explorer,
        on_about=open_about,
        skip_default=st.session_state.lme_skip_preference,
        on_skip_change=on_skip_welcome_change,
    )
    st.stop()

# New Explorer sessions begin with one chart. Existing user selections persist.
# The ui.py header accepts this semantic value without any modification.
st.session_state.setdefault("chart_layout", "Single")

# Main Explorer
layout_mode, view_mode = render_header(show_layout_control=True)

# V12.2: detect only the screen class with a tiny, invisible v2 component.
# Keep numeric Altair heights: Vega-Lite's `height="container"` caused
# zero-height plots in the earlier experiment. This does not affect styling.
# The component is mounted only in Explorer, and resize/orientation changes
# are reported to Python (avoiding forced reloads and URL query parameters).
_LME_VIEWPORT_JS = """
export default function({ data, setStateValue }) {
    let lastMode = data?.previousMode ?? "desktop";
    let debounceId;

    const reportViewport = () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        // Both phone orientations qualify, but a desktop/laptop does not.
        // These are CSS pixels; DevTools mobile emulation uses them too.
        const phoneSized = Math.min(width, height) <= 600
            && Math.max(width, height) <= 1000;
        const mode = !phoneSized ? "desktop"
            : (width > height ? "landscape" : "portrait");
        if (mode !== lastMode) {
            lastMode = mode;
            setStateValue("mode", mode);
        }
    };

    const onResize = () => {
        window.clearTimeout(debounceId);
        debounceId = window.setTimeout(reportViewport, 180);
    };

    reportViewport();
    window.addEventListener("resize", onResize);
    return () => {
        window.removeEventListener("resize", onResize);
        window.clearTimeout(debounceId);
    };
}
"""

_lme_viewport_component = st.components.v2.component(
    "lme_explorer_viewport_v12_2", js=_LME_VIEWPORT_JS
)
_lme_viewport_result = _lme_viewport_component(
    key="lme_explorer_viewport_v12_2",
    data={"previousMode": st.session_state.get("lme_last_viewport_mode", "desktop")},
    default={"mode": "desktop"},
    on_mode_change=lambda: None,
    height=0,
)
_lme_viewport_mode = _lme_viewport_result.mode
if _lme_viewport_mode not in ("portrait", "landscape", "desktop"):
    _lme_viewport_mode = "desktop"
st.session_state["lme_last_viewport_mode"] = _lme_viewport_mode
CHART_HEIGHT = {"portrait": 260, "landscape": 200, "desktop": 380}[_lme_viewport_mode]
# V12.6: on phone-sized screens, keep charts readable and tooltip-enabled
# without Altair's pan/zoom selection capturing swipe and pinch gestures.
# Desktop charts retain their existing pan/zoom behavior.
ENABLE_CHART_PAN_ZOOM = _lme_viewport_mode == "desktop"

# Explorer only: V9 placement for Streamlit's NATIVE Altair toolbar.
# Keep the V6 chart spacing and stable hover behaviour; move only the toolbar
# above the plotting surface in One/Two views. Overlay has its own title-row offset.
# This uses Streamlit DOM selectors and requires visual browser verification.
st.html(
    """<style>
    @media (min-width: 1061px) {
        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        [data-testid="stArrowVegaLiteChart"] {
            padding-top: 36px !important;
            box-sizing: border-box !important;
        }

        /* Keep normal widget coordinates; no negative chart margins. */
        :is(.st-key-chart_a, .st-key-chart_b)
        [data-testid="stArrowVegaLiteChart"] {
            margin-top: 0 !important;
            overflow: visible !important;
        }

        /* The chart and toolbar should be able to paint above the plot. */
        :is(.st-key-chart_a, .st-key-chart_b)
        :is([data-testid="stVegaLiteChart"],
            [data-testid="stArrowVegaLiteChart"]) {
            overflow: visible !important;
        }

        /* V6 stable positioning, including the hover state. */
        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        :is([data-testid="stElementToolbar"], .stElementToolbar),
        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        :is([data-testid="stElementToolbar"], .stElementToolbar):hover {
            position: absolute !important;
            top: 8px !important;
            right: 8px !important;
            bottom: auto !important;
            left: auto !important;
            inset: 8px 8px auto auto !important;
            margin: 0 !important;
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
            transform: none !important;
            translate: none !important;
            transition: none !important;
            animation: none !important;
            z-index: 10 !important;
        }

        /* V9: tested in DevTools: inset, not top alone, controls placement.
           Position beside the title; keep identical hover coordinates. */
        :is(.st-key-chart_a, .st-key-chart_b)
        :is([data-testid="stElementToolbar"], .stElementToolbar),
        :is(.st-key-chart_a, .st-key-chart_b)
        :is([data-testid="stElementToolbar"], .stElementToolbar):hover {
            top: -42px !important;
            inset: -42px 0px auto auto !important;
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        /* Remove the native white toolbar pill on the grey chart card. */
        :is(.st-key-chart_a, .st-key-chart_b)
        [data-testid="stElementToolbarButtonContainer"] {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        /* V10: Overlay has two text rows above the combined plot. Raise its
           toolbar separately beside the A/B selection summary. Verify the
           -56px offset visually at the target desktop window width. */
        .st-key-combined_chart
        :is([data-testid="stElementToolbar"], .stElementToolbar),
        .st-key-combined_chart
        :is([data-testid="stElementToolbar"], .stElementToolbar):hover {
            top: -42px !important;
            right: 0 !important;
            inset: -42px 0px auto auto !important;
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        .st-key-combined_chart
        [data-testid="stElementToolbarButtonContainer"] {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        :is([data-testid="stElementToolbar"], .stElementToolbar)
        :is(button, [data-testid="stElementToolbarButton"]) {
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }

        /* Fullscreen must never retain the negative toolbar offset. */
        :fullscreen
        [data-testid="stArrowVegaLiteChart"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        :fullscreen
        :is([data-testid="stElementToolbar"], .stElementToolbar),
        :fullscreen
        :is([data-testid="stElementToolbar"], .stElementToolbar):hover {
            background: white !important;
            top: 8px !important;
            right: 8px !important;
            inset: 8px 8px auto auto !important;
        }
    }
    </style>"""
)

# V12.7 (mobile only): keep Streamlit's native Fullscreen chart action visible.
# Scope to chart cards and leave the established desktop toolbar CSS untouched.
# The button's aria-label="Fullscreen" was verified in browser DevTools.
# :has() selects the button wrapper without relying on Streamlit's button order.
if _lme_viewport_mode in ("portrait", "landscape"):
    st.html(
        """<style>
        /* Keep the one remaining action in the title row, ABOVE the chart.
           The native toolbar otherwise sits partly behind the Vega plot. */
        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        :is([data-testid="stFullScreenFrame"], [data-testid="stArrowVegaLiteChart"]) {
            overflow: visible !important;
        }

        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        :is([data-testid="stElementToolbar"], .stElementToolbar) {
            position: absolute !important;
            inset: -42px 0 auto auto !important;
            margin: 0 !important;
            z-index: 30 !important;
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
            transform: none !important;
            transition: none !important;
        }

        /* A single icon, rather than a large white Streamlit toolbar pill. */
        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        [data-testid="stElementToolbarButtonContainer"] {
            background: transparent !important;
            box-shadow: none !important;
            border: 0 !important;
            padding: 0 !important;
        }

        /* In fullscreen, restore the toolbar to its normal screen corner. */
        :fullscreen :is([data-testid="stElementToolbar"], .stElementToolbar) {
            inset: 8px 8px auto auto !important;
            z-index: 50 !important;
        }
        :fullscreen [data-testid="stElementToolbarButtonContainer"] {
            background: white !important;
        }

        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        [data-testid="stElementToolbarButtonContainer"]
        > [data-testid="stElementToolbarButton"] {
            display: none !important;
        }

        :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
        [data-testid="stElementToolbarButtonContainer"]
        > [data-testid="stElementToolbarButton"]:has(button[aria-label*="fullscreen" i]) {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }

        /* V18 mobile: keep the Fullscreen icon on its tested title row as
           the space below that row increases by 8px. For Overlay, keep it
           alongside the FIRST legend row, INSIDE the black chart card.
           Actual browser fullscreen retains the 8px screen-corner inset. */
        body:not(:has(:fullscreen))
        .st-key-combined_chart
        :is([data-testid="stElementToolbar"], .stElementToolbar) {
            inset: -66px 0 auto auto !important;
        }
        </style>"""
    )

# Indicator buttons live beneath each chart and act as its interactive legend.
# On narrow screens show two legend items per row, never four vertical blocks.
st.html(
    """<style>
    /* Compact gap below the Explorer toolbar on wide screens only. */
    @media (min-width: 1061px) {
        .st-key-lme_explorer_toolbar {
            margin-bottom: 0 !important;
            padding-bottom: 0.3rem !important;
        }
    }
    /* One outer card for Controls + Chart. Internal keyed containers keep
       their existing state and responsive selectors, without extra frames. */
    .st-key-analysis_a .st-key-controls_a,
    .st-key-analysis_b .st-key-controls_b {
        border: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        border-radius: 0 !important;
    }
    .st-key-analysis_a .st-key-chart_a,
    .st-key-analysis_b .st-key-chart_b {
        border: 0 !important;
        border-top: 1px solid var(--lme-border, #e2e5e9) !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        margin-top: 0 !important;
        padding-top: 0.55rem !important;
    }
    [class*="st-key-indicator_legend_"] [class*="st-key-indicator_button_"] button {
        min-height: 32px !important;
        padding: 0.2rem 0.15rem !important;
        white-space: nowrap !important;
    }
    [class*="st-key-indicator_legend_"] [class*="st-key-indicator_button_"] button p {
        white-space: nowrap !important;
        font-size: 0.86rem !important;
    }
    @media (max-width: 768px) {
        [class*="st-key-indicator_legend_"] [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
            gap: 0.1rem 0.5rem !important;
        }
        [class*="st-key-indicator_legend_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 0 0 calc(50% - 0.25rem) !important;
            width: calc(50% - 0.25rem) !important;
            max-width: calc(50% - 0.25rem) !important;
            min-width: 0 !important;
        }
    }
    </style>""",
)

# Qualification level uses a light text-only horizontal selector.
# Scope the overrides to the qualification widgets so the toolbar and
# any other segmented controls retain their existing appearance.
st.html(
    """<style>
    div[class*="st-key-qualification_tabs_"] [data-testid="stSegmentedControl"] {
        max-width: 100%;
        overflow-x: auto;
        scrollbar-width: thin;
    }
    div[class*="st-key-qualification_tabs_"] [data-testid="stSegmentedControl"]
    [role="group"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        width: max-content !important;
        max-width: none !important;
        gap: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"] {
        background: transparent !important;
        color: #667085 !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        white-space: nowrap !important;
        flex: 0 0 auto !important;
        font-weight: 500 !important;
        padding: 0.28rem 0.65rem !important;
    }
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"]:not(:last-child) {
        border-right: 1px solid #d5d9df !important;
    }
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"][data-selected="true"] {
        background: transparent !important;
        color: #171717 !important;
        font-weight: 700 !important;
    }
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"]:hover {
        background: #e9ebef !important;
        color: #171717 !important;
    }
    /* On phones, keep the five qualification levels on one line. If a
       particularly narrow display cannot fit them, allow horizontal scroll
       instead of wrapping Expert onto a second row. */
    @media (max-width: 600px) {
        div[class*="st-key-qualification_tabs_"] [data-testid="stSegmentedControl"] {
            overflow-x: auto !important;
            overflow-y: hidden !important;
            max-width: 100% !important;
            -webkit-overflow-scrolling: touch;
        }
        div[class*="st-key-qualification_tabs_"] [data-testid="stSegmentedControl"]
        [role="group"] {
            flex-wrap: nowrap !important;
            width: max-content !important;
            min-width: max-content !important;
        }
        div[class*="st-key-qualification_tabs_"]
        button[data-variant="segmented_control"] {
            /* Comfortable tap spacing; the row scrolls if it does not fit. */
            padding: 0.34rem 0.55rem !important;
            font-size: 0.86rem !important;
        }
    }
    </style>""",
)


# V13 navigator presentation only. Kept separate from the existing chart CSS.
st.html(
    """<style>
    /* Dark Slate controls, scoped to the new Occupation Navigator only. */
    div[class*="st-key-occupation_picker_row_"] [data-testid="stPopover"] button {
        width: 100% !important;
        min-width: 0 !important;
        min-height: 38px !important;
        background: #2d3b4c !important;
        border: 1px solid #586c82 !important;
        border-radius: 9px !important;
        box-shadow: none !important;
        color: #f5f8fc !important;
        justify-content: flex-start !important;
        overflow: hidden !important;
    }
    div[class*="st-key-occupation_picker_row_"] [data-testid="stPopover"] button :is(p, span) {
        color: #f5f8fc !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-width: 0 !important;
    }
    div[class*="st-key-occupation_picker_row_"] [data-testid="stPopover"] button:hover {
        background: #35465a !important;
        border-color: #8b9fb8 !important;
    }
    div[class*="st-key-occupation_picker_row_"] [data-testid="stPopover"] button:disabled {
        opacity: 0.52 !important;
        cursor: not-allowed !important;
    }
    div[class*="st-key-occupation_back_"] button {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        color: #f5f8fc !important;
        white-space: nowrap !important;
        padding: 0.15rem 0.25rem !important;
        min-height: 30px !important;
    }
    div[class*="st-key-occupation_back_"] button:disabled {
        opacity: 0.4 !important;
    }
    /* The Back button belongs at the card's right edge, not centered in a
       wide trailing column. Keep its narrow-width phone behavior unchanged. */
    @media (min-width: 769px) {
        /* Keep Occupation and Back in the SAME row on desktop.
           Only scope this to the navigator heading, not chart columns. */
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:last-child {
            flex: 0 0 65px !important;
            width: 65px !important;
            min-width: 65px !important;
            max-width: 65px !important;
        }
    }
    /* Widen the opened picker, not the permanent controls row. */
    body:has(.st-key-lme_explorer_toolbar)
    [data-testid="stPopoverBody"]:has(.lme-v13-occupation-popup-marker) {
        width: min(490px, calc(100vw - 24px)) !important;
        max-width: calc(100vw - 24px) !important;
        background: #293746 !important;
        border: 1px solid #65758a !important;
        border-radius: 10px !important;
        box-shadow: 0 12px 28px rgba(12, 22, 34, 0.22) !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    [data-testid="stPopoverBody"]:has(.lme-v13-occupation-popup-marker)
    :is(p, span, label) {
        color: #f5f8fc !important;
    }
    /* Dark recessed search field inside the expanded popover. */
    body:has(.st-key-lme_explorer_toolbar)
    [data-testid="stPopoverBody"]:has(.lme-v13-occupation-popup-marker)
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #2d3b4c !important;
        border: 1px solid #586c82 !important;
        border-radius: 9px !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    [data-testid="stPopoverBody"]:has(.lme-v13-occupation-popup-marker)
    [data-testid="stSelectbox"] [role="combobox"] {
        background: #2d3b4c !important;
        color: #f5f8fc !important;
    }
    /* Streamlit may stack columns on a phone; retain Search + Browse in one row. */
    @media (max-width: 768px) {
        div[class*="st-key-occupation_picker_row_"] [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0.45rem !important;
        }
        div[class*="st-key-occupation_picker_row_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:first-child {
            min-width: 0 !important;
            width: auto !important;
            flex: 1 1 0 !important;
        }
        div[class*="st-key-occupation_picker_row_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:last-child {
            min-width: 96px !important;
            width: 96px !important;
            max-width: 96px !important;
            flex: 0 0 96px !important;
        }
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
        }
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:first-child {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
        div[class*="st-key-occupation_heading_"] [data-testid="stHorizontalBlock"]
        > [data-testid="stColumn"]:last-child {
            flex: 0 0 76px !important;
            width: 76px !important;
            max-width: 76px !important;
            min-width: 76px !important;
        }
    }
    </style>"""
)


# V15 mobile navigator: ONE real selectbox, no Streamlit popover.
# Desktop controls and chart rendering remain untouched.
if _lme_viewport_mode in ("portrait", "landscape"):
    st.html("""<style>
    /* Keep a single wide native selectbox and a finger-sized mode toggle. */
    div[class*="st-key-occupation_picker_row_"]
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
        flex: 0 0 44px !important;
        width: 44px !important;
        min-width: 44px !important;
        max-width: 44px !important;
    }
    div[class*="st-key-occupation_picker_row_"]
    [data-testid="stSelectbox"] {
        min-width: 0 !important;
        width: 100% !important;
    }
    div[class*="st-key-occupation_picker_row_"]
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        min-height: 40px !important;
        background-color: #2d3b4c !important;
        border: 1px solid #586c82 !important;
        border-radius: 9px !important;
    }
    div[class*="st-key-occupation_picker_row_"]
    [data-testid="stSelectbox"] [data-baseweb="select"] :is(input,span,svg) {
        color: #f5f8fc !important;
    }
    div[class*="st-key-mobile_occupation_mode_"] button {
        width: 44px !important;
        min-width: 44px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        background: #2d3b4c !important;
        color: #f5f8fc !important;
        border: 1px solid #586c82 !important;
        border-radius: 9px !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
    }
    div[class*="st-key-mobile_occupation_mode_"] button p {
        font-size: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
    /* V15.1: simplified hierarchy symbol. Thin strokes and generous internal
       space read better at actual phone size than the previous dense glyph. */
    div[class*="st-key-mobile_occupation_mode_"] button::before {
        content: "";
        display: block;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        margin: 0 !important;
        width: 22px;
        height: 22px;
        background: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%23eaf0f6%22%20stroke-width%3D%221.7%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Crect%20x%3D%229.5%22%20y%3D%222.5%22%20width%3D%225%22%20height%3D%224.5%22%20rx%3D%221.2%22%2F%3E%3Cpath%20d%3D%22M12%207v4.5M5.5%2015v-3.5h13V15%22%2F%3E%3Crect%20x%3D%222.5%22%20y%3D%2215%22%20width%3D%226%22%20height%3D%225.5%22%20rx%3D%221.2%22%2F%3E%3Crect%20x%3D%2215.5%22%20y%3D%2215%22%20width%3D%226%22%20height%3D%225.5%22%20rx%3D%221.2%22%2F%3E%3C%2Fsvg%3E") center / contain no-repeat;
    }
    div[class*="st-key-mobile_occupation_mode_"] button:hover {
        background: #35465a !important;
        border-color: #8194ab !important;
    }
    /* Selected = same muted palette as the qualification controls; one border,
       no doubled white rim or glow. This does not change the mode logic. */
    div[class*="st-key-mobile_occupation_mode_"] button[kind="primary"],
    div[class*="st-key-mobile_occupation_mode_"] button[data-testid="stBaseButton-primary"] {
        background: #52677f !important;
        border: 1px solid #a1b2c7 !important;
        box-shadow: none !important;
    }
    div[class*="st-key-mobile_occupation_mode_"] button[kind="primary"]:hover,
    div[class*="st-key-mobile_occupation_mode_"] button[data-testid="stBaseButton-primary"]:hover {
        background: #5d738c !important;
    }
    /* Touch focus must not look like a second active-state border.
       Keep an explicit outline for keyboard navigation. */
    div[class*="st-key-mobile_occupation_mode_"] button:focus:not(:focus-visible) {
        outline: none !important;
        box-shadow: none !important;
    }
    div[class*="st-key-mobile_occupation_mode_"] button:focus-visible {
        outline: 2px solid #d6e3f1 !important;
        outline-offset: 2px !important;
    }
    </style>""")

# V11a visual theme experiment. Local preview only; V10 chart toolbar rules,
# chart data and widget behavior are deliberately left unchanged.
# To revert: remove this single st.html block.
st.html(
    """<style>
    :root {
        /* A subtle blue-gray tint, sampled from the panel border color. */
        --lme-preview-page-tint: rgba(89, 107, 128, 0.12);
        --lme-preview-card: #394758;
        --lme-preview-card-border: #596b80;
        --lme-preview-input: #2d3b4c;
        --lme-preview-input-border: #586c82;
        --lme-preview-tab: #485a70;
        --lme-preview-tab-active: #6c8099;
        --lme-preview-chart: #f4f6f8;
        --lme-preview-foreground: #f5f8fc;
        --lme-preview-shadow: 0 10px 26px rgba(20, 30, 45, 0.17),
                              0 2px 6px rgba(20, 30, 45, 0.09);
    }

    /* Explorer page only: slightly darker, cooler outer canvas.
       The original #f3f4f6 remains unchanged on Welcome and About. */
    .stApp:has(.st-key-lme_explorer_toolbar) {
        background: linear-gradient(
            var(--lme-preview-page-tint),
            var(--lme-preview-page-tint)
        ), #f3f4f6 !important;
    }

    /* V12.5 mobile spacing experiment: reduce only the Explorer page's
       left/right margins from the ui.py default 1rem (16px) to 8px.
       Keep the internal card padding, borders, shadows, charts and toolbar. */
    @media (max-width: 900px) {
        .stMainBlockContainer:has(.st-key-lme_explorer_toolbar) {
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
    }

    /* Outer One/Two cards and the three bordered Overlay panels.
       Covers both the keyed content and Streamlit's surrounding border wrapper. */
    :is(.st-key-analysis_a, .st-key-analysis_b, .st-key-combined_chart,
        .st-key-controls_a, .st-key-controls_b) {
        background-color: var(--lme-preview-card) !important;
        color: var(--lme-preview-foreground) !important;
    }
    /* Attach the shadow to the actual keyed cards, rather than depending
       on which side of the card Streamlit puts its border wrapper. */
    :is(.st-key-analysis_a, .st-key-analysis_b, .st-key-combined_chart,
        .st-key-controls_a, .st-key-controls_b) {
        border-radius: 14px !important;
        box-shadow: var(--lme-preview-shadow) !important;
    }
    /* One/Two contains a controls child: it must not cast a second shadow. */
    .st-key-analysis_a .st-key-controls_a,
    .st-key-analysis_b .st-key-controls_b {
        box-shadow: none !important;
    }
    /* Keep a distinct border where Streamlit draws one. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    [data-testid="stVerticalBlockBorderWrapper"]:has(
        :is(.st-key-analysis_a, .st-key-analysis_b,
            .st-key-combined_chart, .st-key-controls_a, .st-key-controls_b)
    ) {
        background-color: var(--lme-preview-card) !important;
        border-color: var(--lme-preview-card-border) !important;
    }

    /* In One/Two the controls are part of the outer card, not extra cards. */
    .st-key-analysis_a .st-key-controls_a,
    .st-key-analysis_b .st-key-controls_b {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    .st-key-analysis_a .st-key-chart_a,
    .st-key-analysis_b .st-key-chart_b {
        background: transparent !important;
        border-top-color: #718096 !important;
    }

    /* Titles, filter labels, Overlay headings and interactive legends. */
    :is(.st-key-controls_a, .st-key-controls_b,
        .st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    :is(p, span, label) {
        color: var(--lme-preview-foreground) !important;
    }
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button,
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button :is(p, span) {
        color: var(--lme-preview-foreground) !important;
    }

    /* Search and Browse: darker, recessed fields. Cover nested selectbox
       nodes as Streamlit may paint the visible input on an inner element. */
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] :is(
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        [data-baseweb="select"] > div > div,
        [role="combobox"]
    ) {
        background-color: var(--lme-preview-input) !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border: 1px solid var(--lme-preview-input-border) !important;
        border-radius: 9px !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] :is(input, span, svg, [role="combobox"]) {
        color: var(--lme-preview-foreground) !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] input::placeholder {
        color: #e4eaf2 !important;
        opacity: 1 !important;
    }

    /* V11a.4: keep the proven V11a.2 dark input rule above.  In the
       installed Streamlit/BaseWeb build, the arrow section is painted by
       deeper descendants; paint them the SAME dark color, not transparent.
       This affects only the two Explorer occupation Selectboxes. */
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"] > div * {
        background-color: var(--lme-preview-input) !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"] :is(input, span, svg) {
        color: var(--lme-preview-foreground) !important;
        caret-color: var(--lme-preview-foreground) !important;
    }

    /* Quiet visible keyboard focus, overriding the Streamlit red ring. */
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    :is(.st-key-controls_a, .st-key-controls_b)
    [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within {
        outline: 0 !important;
        border-color: #a6b8ce !important;
        box-shadow: 0 0 0 2px #a6b8ce !important;
    }

    /* The dropdown is rendered in a body-level portal by BaseWeb, outside
       .st-key-controls_*.  These rules activate only on Explorer pages. */
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"]) {
        background-color: var(--lme-preview-input) !important;
        color: var(--lme-preview-foreground) !important;
        border-color: var(--lme-preview-input-border) !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"])
    :is(div, ul, li, [role="option"], p, span) {
        background-color: var(--lme-preview-input) !important;
        color: var(--lme-preview-foreground) !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"])
    :is([role="option"], li, [data-baseweb="option"]):is(
        :hover, [aria-selected="true"], [data-highlighted="true"]
    ),
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"])
    :is([role="option"], li, [data-baseweb="option"]):is(
        :hover, [aria-selected="true"], [data-highlighted="true"]
    ) :is(div, p, span) {
        background-color: #53677f !important;
        color: #ffffff !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"])
    input {
        background: #394b60 !important;
        color: var(--lme-preview-foreground) !important;
        caret-color: #fff !important;
    }
    body:has(.st-key-lme_explorer_toolbar)
    :is([data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"])
    input::placeholder {
        color: #dbe4ee !important;
        opacity: 1 !important;
    }

    /* Qualification tabs are brighter than the input fields. */
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"] {
        background: var(--lme-preview-tab) !important;
        color: var(--lme-preview-foreground) !important;
        border-right-color: #7b8aa0 !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"][data-selected="true"] {
        background: var(--lme-preview-tab-active) !important;
        color: #fff !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"]:hover {
        background: #657991 !important;
        color: #fff !important;
    }

    /* Plot stays light, including the actual Vega drawing surface.
       The Vega axis labels retain their existing dark chart theme. */
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [data-testid="stVegaLiteChart"],
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [data-testid="stVegaLiteChart"] .vega-embed,
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [data-testid="stVegaLiteChart"] .vega-embed :is(canvas, svg) {
        background-color: var(--lme-preview-chart) !important;
    }

    /* Only recolor native chart tools for the dark surrounding card.
       Position, visibility, hover behavior and fullscreen offsets are V10. */
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    :is([data-testid="stElementToolbar"], .stElementToolbar) button,
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    :is([data-testid="stElementToolbar"], .stElementToolbar) button svg {
        color: #f2f5fa !important;
    }
    :fullscreen :is([data-testid="stElementToolbar"], .stElementToolbar)
    button,
    :fullscreen :is([data-testid="stElementToolbar"], .stElementToolbar)
    button svg {
        color: #243245 !important;
    }
    /* Qualification buttons: reuse the Occupation input palette.
       Natural widths, separate rounded buttons, no overlap. */
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] [data-testid="stSegmentedControl"] [role="group"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        width: max-content !important;
        min-width: max-content !important;
        max-width: none !important;
        /* The native segmented-control markup can wrap individual buttons.
           A gap here alone does not reliably separate the visible buttons. */
        gap: 0 !important;
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"] {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: max-content !important;
        /* Margin on the button itself also works when Streamlit inserts
           intermediate wrappers between the group and its buttons. */
        margin: 0 5px 0 0 !important;
        padding: 0.34rem 0.76rem !important;
        justify-content: center !important;
        text-align: center !important;
        background: #485A70 !important;
        color: #F5F8FC !important;
        border: 0 !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"] :is(p, span) {
        color: inherit !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"]:hover {
        background: #35465A !important;
        color: #FFFFFF !important;
    }
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"][data-selected="true"],
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"][data-selected="true"]:hover {
        background: #6C8099 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    @media (max-width: 600px) {
        :is(.st-key-controls_a, .st-key-controls_b)
        div[class*="st-key-qualification_tabs_"] button[data-variant="segmented_control"] {
            font-size: 0.78rem !important;
            padding: 0.34rem 0.60rem !important;
        }
    }

    </style>"""
)

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



# V17 mobile-only indicator toggles: a single black chart surface with
# subtly outlined touch targets, centered in a symmetrical 2 x 2 grid.
# The public st.button(type=...) flag distinguishes enabled/disabled styles;
# no changes to data, click handlers, desktop labels or Vega/Altair charts.
if _lme_viewport_mode in ("portrait", "landscape"):
    st.html("""<style>
    /* V18: reduce the plot-to-legend spacing by 8px. This adjustment is
       local to chart cards; Streamlit's other vertical gaps stay intact. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_legend_"] {
        margin-top: -8px !important;
    }

    /* Streamlit's four-column layout becomes a true centered 2 x 2 grid,
       also on phones in landscape orientation. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    [class*="st-key-indicator_legend_"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        column-gap: 8px !important;
        row-gap: 8px !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    [class*="st-key-indicator_legend_"] [data-testid="stHorizontalBlock"]
    > [data-testid="stColumn"] {
        flex: 0 0 calc(50% - 4px) !important;
        width: calc(50% - 4px) !important;
        min-width: 0 !important;
        max-width: calc(50% - 4px) !important;
    }

    /* Neither ON nor OFF uses a contrasting button fill. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button {
        width: 100% !important;
        min-height: 44px !important;
        padding: 7px 5px !important;
        background: #0e1117 !important;
        color: #f5f8fc !important;
        border: 1px solid #46515e !important;
        border-radius: 9px !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button :is(p, span) {
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: #f5f8fc !important;
        white-space: nowrap !important;
        text-align: center !important;
    }

    /* Disabled: same black, softer border, hollow marker, dimmed label. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button[data-testid="stBaseButton-secondary"] {
        border-color: #313a46 !important;
        color: #8b96a4 !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button[data-testid="stBaseButton-secondary"] :is(p, span) {
        color: #8b96a4 !important;
    }

    /* Preserve subtle interaction feedback without coloring the button. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button:hover {
        border-color: #8796a9 !important;
        background: #0e1117 !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-chart_a, .st-key-chart_b, .st-key-combined_chart)
    [class*="st-key-indicator_button_"] button:focus-visible {
        outline: 2px solid #a6b8ce !important;
        outline-offset: 2px !important;
    }
    </style>""")


# Same indicator configuration as the existing charts. The dots and names
# appear only below the plots; each legend item is also a toggle button.
INDICATOR_LEGEND = (
    ("Vacancies", "🔴"),
    ("Employed", "🔵"),
    ("Unemployed", "🟡"),
    ("Job seekers", "🟢"),
)


def render_indicator_legend(chart_container, chart_number: int, group: str = "") -> None:
    """Interactive four-item legend below a chart (or A/B legends in Overlay)."""
    legend = chart_container.container(key=f"indicator_legend_{chart_number}")
    if group:
        legend.caption(f"Selection {group}")

    legend_columns = legend.columns(4, gap="small")
    mobile_legend = _lme_viewport_mode in ("portrait", "landscape")
    for column, (label, dot) in zip(legend_columns, INDICATOR_LEGEND):
        state_key = f"indicator_state_{chart_number}_{label}"
        is_selected = st.session_state.get(state_key, label != "Job seekers")
        button_label = f"{dot}  {label}" if is_selected else f"◯  {label}"
        if column.button(
            button_label,
            key=f"indicator_button_{chart_number}_{label}",
            help=f"{'Hide' if is_selected else 'Show'} {label.lower()}",
            type="primary" if mobile_legend and is_selected else "secondary",
            width="stretch",
        ):
            st.session_state[state_key] = not is_selected
            st.rerun()


# Overlay uses a separate, shared indicator selection. Initialize it only once
# from the union of the current independent A/B choices. Never write back to A/B.
def ensure_overlay_indicators() -> None:
    if st.session_state.get("overlay_indicators_initialized", False):
        return
    for label, _ in INDICATOR_LEGEND:
        a = bool(st.session_state.get(f"indicator_state_1_{label}", label != "Job seekers"))
        b = bool(st.session_state.get(f"indicator_state_2_{label}", label != "Job seekers"))
        st.session_state[f"overlay_indicator_{label}"] = a or b
    st.session_state["overlay_indicators_initialized"] = True


def render_overlay_indicator_legend(chart_container) -> None:
    legend = chart_container.container(key="indicator_legend_overlay")
    columns = legend.columns(4, gap="small")
    mobile_legend = _lme_viewport_mode in ("portrait", "landscape")
    for column, (label, dot) in zip(columns, INDICATOR_LEGEND):
        state_key = f"overlay_indicator_{label}"
        enabled = bool(st.session_state.get(state_key, False))
        if column.button(
            f"{dot}  {label}" if enabled else f"◯  {label}",
            key=f"indicator_button_overlay_{label}",
            help=f"{'Hide' if enabled else 'Show'} {label.lower()} for both occupations",
            type="primary" if mobile_legend and enabled else "secondary",
            width="stretch",
        ):
            st.session_state[state_key] = not enabled
            st.rerun()


def render_chart(
    chart_number: int,
    controls_container,
    chart_container,
    render_output: bool = True,
    indicator_override: dict[str, bool] | None = None,
):

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
    GERMANY_LABEL = "All occupations"


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
    # V13 preview — compact Occupation Navigator
    # ---------------------------------------------------------
    # Preserve the semantic occupation state used by the charts. Search and
    # Browse are two different paths to the same selected occupation code.
    # Each analysis (A/B) has its own widget keys and selection state.

    selected_code = str(st.session_state[selected_code_key])
    search_names = dict(
        zip(
            occupations["occupation_code"].astype(str),
            occupations["occupation_name"].astype(str),
        )
    )
    selected_label = (
        GERMANY_LABEL
        if selected_code == GERMANY_CODE
        else search_names.get(selected_code, selected_code)
    )
    child_rows = get_children(None if selected_code == GERMANY_CODE else selected_code)
    has_children = not child_rows.empty

    # Mobile: browsing location is separate from the profession being graphed.
    # This prevents a mode switch from silently changing the chart selection.
    mobile_picker = _lme_viewport_mode in ("portrait", "landscape")
    mode_key = f"mobile_occupation_view_{chart_number}"
    browse_parent_key = f"mobile_occupation_browse_parent_{chart_number}"
    if mobile_picker:
        st.session_state.setdefault(mode_key, "search")
        st.session_state.setdefault(browse_parent_key, GERMANY_CODE)
    category_mode = mobile_picker and st.session_state[mode_key] == "categories"

    # Keep the classification position in session state for Back navigation;
    # it does not need a separate breadcrumb row in the compact mobile UI.
    browse_parent = str(st.session_state.get(browse_parent_key, GERMANY_CODE))
    if mobile_picker and browse_parent != GERMANY_CODE and get_occupation_row(browse_parent) is None:
        browse_parent = GERMANY_CODE
        st.session_state[browse_parent_key] = browse_parent

    # First row: keep the established heading and Back placement.
    heading = controls.container(key=f"occupation_heading_{chart_number}")
    caption_col, back_col = heading.columns(
        [12, 1], gap="small", vertical_alignment="center"
    )
    # Single-line heading in Search and Categories modes (no breadcrumb row).
    heading_label = (
        "Occupation · Subcategories" if category_mode and browse_parent != GERMANY_CODE
        else "Occupation · Categories" if category_mode
        else "Occupation:"
    )
    caption_col.markdown(
        f'<span style="font-size:0.86rem;font-weight:600;">'
        f'{heading_label}</span>',
        unsafe_allow_html=True,
    )
    if back_col.button(
        "‹ Back",
        key=f"occupation_back_{chart_number}",
        type="tertiary",
        disabled=selected_code == GERMANY_CODE and not category_mode,
        width="stretch",
        help=("Previous category, or return to Search" if category_mode
              else "Go to the parent occupation category"),
    ):
        if category_mode:
            nav_parent = st.session_state[browse_parent_key]
            if nav_parent == GERMANY_CODE:
                st.session_state[mode_key] = "search"
            else:
                parent_code = get_parent_code(nav_parent)
                new_parent = str(parent_code) if parent_code is not None else GERMANY_CODE
                st.session_state[browse_parent_key] = new_parent
                st.session_state[selected_code_key] = new_parent
        else:
            parent_code = get_parent_code(selected_code)
            st.session_state[selected_code_key] = (
                str(parent_code) if parent_code is not None else GERMANY_CODE
            )
        st.rerun()

    # Desktop: two independent native dropdowns, unchanged.
    # Mobile: one shared popover and a 44px Folder Tree mode button.
    pickers = controls.container(key=f"occupation_picker_row_{chart_number}")
    search_col, browse_col = pickers.columns(
        [5, 1] if mobile_picker else [1, 1],
        gap="small",
        vertical_alignment="center",
    )

    child_names = dict(
        zip(
            child_rows["occupation_code"].astype(str),
            child_rows["occupation_name"].astype(str),
        )
    )

    if not mobile_picker:
        # Show the *actual selection*, rather than a transient Search prompt.
        # Tying widget keys to the semantic code lets Back / Browse update the
        # displayed value without trying to mutate an existing widget key.
        search_options = [GERMANY_CODE] + list(search_names)
        desktop_search_key = (
            f"v13_desktop_occupation_search_{chart_number}_{selected_code}"
        )

        def on_desktop_search():
            picked = st.session_state.get(desktop_search_key)
            if picked is not None:
                st.session_state[selected_code_key] = str(picked)

        with search_col:
            st.selectbox(
                "Search occupations",
                options=search_options,
                index=(
                    search_options.index(selected_code)
                    if selected_code in search_options else 0
                ),
                format_func=lambda code: (
                    f"🔎 {GERMANY_LABEL}" if code == GERMANY_CODE
                    else search_names[code]
                ),
                key=desktop_search_key,
                on_change=on_desktop_search,
                label_visibility="collapsed",
                width="stretch",
            )

        desktop_browse_key = (
            f"v13_desktop_occupation_browse_{chart_number}_{selected_code}"
        )

        def on_desktop_browse():
            picked = st.session_state.get(desktop_browse_key)
            if picked is not None:
                st.session_state[selected_code_key] = str(picked)

        with browse_col:
            st.selectbox(
                "Categories",
                options=[None] + list(child_names),
                index=0,
                format_func=lambda code: (
                    "Categories" if code is None and has_children
                    else "No further categories" if code is None
                    else child_names[code]
                ),
                key=desktop_browse_key,
                on_change=on_desktop_browse,
                disabled=not has_children,
                label_visibility="collapsed",
                width="stretch",
            )
    else:
        # V15: mobile displays ONE native Streamlit selectbox in the card.
        # The tree icon switches its options; there is NO extra popover panel.
        # Search and Categories intentionally have separate widget identities.
        # Selected occupation remains shared across both modes and charts.
        alphabetical_codes = sorted(
            search_names,
            key=lambda code: (search_names[code].casefold(), code),
        )

        nav_parent = str(st.session_state[browse_parent_key])
        nav_label = (
            GERMANY_LABEL if nav_parent == GERMANY_CODE
            else search_names.get(nav_parent, nav_parent)
        )
        nav_rows = get_children(None if nav_parent == GERMANY_CODE else nav_parent)
        nav_names = dict(zip(
            nav_rows["occupation_code"].astype(str),
            nav_rows["occupation_name"].astype(str),
        ))

        with search_col:
            if category_mode:
                category_picker_key = f"v15_mobile_category_{chart_number}_{nav_parent}"

                def on_category_occupation():
                    picked = st.session_state.get(category_picker_key)
                    if picked is not None:
                        st.session_state[selected_code_key] = str(picked)
                        st.session_state[browse_parent_key] = str(picked)

                if nav_names:
                    st.selectbox(
                        "Choose a subcategory",
                        options=[None] + list(nav_names),
                        index=0,
                        format_func=lambda code: (
                            ("Categories" if nav_parent == GERMANY_CODE
                             else nav_label) if code is None
                            else nav_names[code]
                        ),
                        key=category_picker_key,
                        on_change=on_category_occupation,
                        label_visibility="collapsed",
                        width="stretch",
                    )
                else:
                    # Native disabled dropdown keeps the single-row layout
                    # at leaf nodes; Back remains available above.
                    st.selectbox(
                        "No further subcategories",
                        options=[nav_label],
                        disabled=True,
                        help="No further subcategories; use Back to go up a level",
                        key=f"v15_mobile_leaf_{chart_number}_{nav_parent}",
                        label_visibility="collapsed",
                        width="stretch",
                    )
            else:
                search_picker_key = (
                    f"v15_mobile_search_{chart_number}_{selected_code}"
                )

                def on_search_occupation():
                    picked = st.session_state.get(search_picker_key)
                    if picked is not None:
                        st.session_state[selected_code_key] = str(picked)

                search_options = [GERMANY_CODE] + alphabetical_codes
                st.selectbox(
                    "Search occupations alphabetically",
                    options=search_options,
                    index=(search_options.index(selected_code)
                           if selected_code in search_options else 0),
                    format_func=lambda code: (
                        f"⌕  {GERMANY_LABEL if code == GERMANY_CODE else search_names[code]}"
                    ),
                    key=search_picker_key,
                    on_change=on_search_occupation,
                    label_visibility="collapsed",
                    width="stretch",
                )

        with browse_col:
            if st.button(
                "Categories",
                key=f"mobile_occupation_mode_{chart_number}",
                type="primary" if category_mode else "secondary",
                help=("Return to alphabetical search" if category_mode
                      else "Browse occupations by category"),
                width="stretch",
            ):
                if category_mode:
                    st.session_state[mode_key] = "search"
                else:
                    # Enter near the selected occupation, or at its parent
                    # when the selected code is a leaf.
                    candidate = selected_code
                    if candidate != GERMANY_CODE and get_children(candidate).empty:
                        candidate = get_parent_code(candidate) or GERMANY_CODE
                    st.session_state[browse_parent_key] = str(candidate)
                    st.session_state[mode_key] = "categories"
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


    # Display names only: filtering keeps the original BA qualification values.
    QUALIFICATION_DISPLAY_LABELS = {
        "Insgesamt": "Overall",
        "Gesamt": "Overall",
        "Helfer": "Helpers",
        "Fachkraft": "Skilled",
        "Spezialist": "Specialists",
        "Experte": "Experts",
    }

    # Compact labels are used only in the qualification selector. Keep the
    # original BA qualification codes and full labels for data and Overlay.
    QUALIFICATION_TAB_LABELS = {
        "Insgesamt": "All",
        "Gesamt": "All",
        "Helfer": "Helper",
        "Fachkraft": "Skilled",
        "Spezialist": "Specialist",
        "Experte": "Expert",
    }

    # Use a human-friendly order rather than alphabetical German sorting.
    qualification_order = (
        "Insgesamt", "Gesamt", "Helfer", "Fachkraft", "Spezialist", "Experte"
    )
    qualification_options = sorted(
        occupation_df["qualification"].dropna().astype(str).unique().tolist(),
        key=lambda q: (
            qualification_order.index(q)
            if q in qualification_order
            else len(qualification_order),
            q,
        ),
    )

    # Keep the semantic choice separate from Streamlit's widget state.
    # Chart B's widget can disappear in Single view, but its choice must persist.
    qualification_state_key = f"selected_qualification_{chart_number}"
    # A new key avoids reusing the old selectbox widget's identity.
    qualification_widget_key = f"qualification_tabs_{chart_number}"
    previous_qualification = st.session_state.get(
        qualification_state_key,
        st.session_state.get(f"qualification_{chart_number}"),
    )

    # These labels can represent the same 'Overall' level in BA datasets.
    if previous_qualification in ("Insgesamt", "Gesamt"):
        previous_qualification = next(
            (q for q in ("Insgesamt", "Gesamt") if q in qualification_options),
            previous_qualification,
        )

    default_qualification = next(
        (q for q in ("Insgesamt", "Gesamt") if q in qualification_options),
        qualification_options[0] if qualification_options else None,
    )
    selected_qualification = (
        previous_qualification
        if previous_qualification in qualification_options
        else default_qualification
    )
    st.session_state[qualification_state_key] = selected_qualification

    if qualification_options:
        # Desktop keeps the visible Qualification label inline. On phone-sized
        # viewports, keep the accessible widget label but omit the extra row.
        if _lme_viewport_mode == "desktop":
            qualification_label_col, qualification_choice_col = controls.columns(
                [1.35, 7.0], gap="small", vertical_alignment="center"
            )
            qualification_label_col.markdown(
                '<span style="font-size: 0.86rem; font-weight: 600; '
                'white-space: nowrap;">Qualification:</span>',
                unsafe_allow_html=True,
            )
        else:
            qualification_choice_col = controls

        # Reconcile old selections before creating the new segmented widget.
        st.session_state[qualification_widget_key] = selected_qualification

        def remember_qualification():
            choice = st.session_state.get(qualification_widget_key)
            if choice in qualification_options:
                st.session_state[qualification_state_key] = choice
            else:
                # Clicking the active tab again must not clear the selection.
                st.session_state[qualification_widget_key] = st.session_state[
                    qualification_state_key
                ]

        selected_qualification = qualification_choice_col.segmented_control(
            "Qualification level",
            options=qualification_options,
            selection_mode="single",
            format_func=lambda q: QUALIFICATION_TAB_LABELS.get(q, q),
            key=qualification_widget_key,
            on_change=remember_qualification,
            disabled=len(qualification_options) == 1,
            label_visibility="collapsed",
            width="content",
        )
        if selected_qualification not in qualification_options:
            selected_qualification = st.session_state[qualification_state_key]
    else:
        if render_output:
            chart_container.warning("No qualification data is available for this occupation.")
        return {
            "plot_df": pd.DataFrame(columns=["report_date", "indicator", "value"]),
            "display_name": selected_name,
            "qualification_label": "No qualification data",
            "chart_number": chart_number,
        }

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

    # Indicator state stays independent for A and B even if one chart is hidden.
    # The controls are now rendered as a legend directly under the chart.
    selected_indicators = []
    for label, indicator in (
        ("Vacancies", "Registered vacancies"),
        ("Employed", "Employed people"),
        ("Unemployed", "Unemployed people"),
        ("Job seekers", "Job seekers"),
    ):
        state_key = f"indicator_state_{chart_number}_{label}"
        if state_key not in st.session_state:
            st.session_state[state_key] = label != "Job seekers"
        enabled = (st.session_state[state_key] if indicator_override is None
                   else indicator_override.get(label, False))
        if enabled:
            selected_indicators.append(indicator)

    if not selected_indicators:
        if render_output:
            chart_container.info("Choose at least one indicator in the legend below.")
            render_indicator_legend(chart_container, chart_number)
        return {
            "plot_df": pd.DataFrame(columns=["report_date", "indicator", "value"]),
            "display_name": selected_name,
            "qualification_label": qualification_label,
            "chart_number": chart_number,
        }

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
        else None
    )

    display_name = (
        "All occupations"
        if selected_occupation_level == 0
        else selected_name
    )

    chart_card = chart_container

    chart_payload = {
        "plot_df": plot_df,
        "display_name": display_name,
        "qualification_label": qualification_label,
        "chart_number": chart_number,
    }
    if not render_output:
        return chart_payload

    # V12.4: keep desktop titles unchanged; mobile titles stay on one line.
    # Reserve room for the native chart toolbar, which sits at the upper right.
    # Truncation affects presentation only: the full occupation name is kept.
    mobile_title = _lme_viewport_mode in ("portrait", "landscape")
    # Align mobile One headings with the two Overlay line-key labels.
    # Keep the desktop title styling and text untouched.
    title_font_size = "15px" if mobile_title else "1.35rem"
    title_max_width = "calc(100% - 108px)" if mobile_title else "100%"
    title_white_space = "nowrap" if mobile_title else "normal"
    # V18 mobile: move 8px of visual breathing room from under the plot
    # to between the heading/Fullscreen row and the plot.
    title_bottom_gap = "16px" if mobile_title else "0.25rem"
    title_overflow = "hidden" if mobile_title else "visible"
    title_ellipsis = "ellipsis" if mobile_title else "clip"
    # The selected qualification materially changes the chart data. Show it
    # in mobile One as we already do in Overlay; do not alter desktop titles.
    if mobile_title and qualification_label:
        short_qualification = {
            "Overall": "All",
            "Helpers": "Helper",
            "Specialists": "Specialist",
            "Experts": "Expert",
        }.get(qualification_label, qualification_label)
        displayed_title = f"{display_name} · {short_qualification}"
    else:
        displayed_title = display_name
    safe_display_name = html.escape(str(displayed_title), quote=True)
    chart_card.markdown(
        f"""
        <div style="
            display: flex;
            align-items: baseline;
            gap: 0.7rem;
            margin-top: 0.15rem;
            margin-bottom: {title_bottom_gap};
            min-width: 0;
        ">
            <span title="{safe_display_name}" style="
                display: block;
                font-size: {title_font_size};
                font-weight: 600;
                line-height: 1.3;
                max-width: {title_max_width};
                white-space: {title_white_space};
                overflow: {title_overflow};
                text-overflow: {title_ellipsis};
                min-width: 0;
            ">{safe_display_name}</span>
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
                    axis=alt.Axis(
                        format=",.0f" if view_mode == "Indexed" else "~s",
                    ),
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
                height=CHART_HEIGHT,
            )
        )
        if ENABLE_CHART_PAN_ZOOM:
            chart = chart.interactive()

        chart_card.altair_chart(
            chart,
            width="stretch",
        )

    render_indicator_legend(chart_container, chart_number)


# Mobile-only visual trial: reduce the inside padding of the Overlay chart
# card to match the Explorer page's outer 8px margins. No desktop changes.
st.html("""<style>
@media (max-width: 768px) {
    .st-key-combined_chart {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
}
</style>""")


# V14.2 mobile-only trial: 8px card spacing with the dark chart area.
# Keep the Occupation controls slate, use the existing phone chart colour for
# the title, plot surround and indicator legend. Overlay already is its own
# chart card; in One, only the chart *portion* of the analysis card changes.
# No chart logic, Vega spec, desktop CSS or desktop layout is modified.
st.html("""<style>
@media (max-width: 600px) and (max-height: 1000px),
       (max-height: 600px) and (max-width: 1000px) {
    /* Pull the first Occupation card closer to the one-line toolbar. */
    .st-key-lme_explorer_toolbar {
        padding-bottom: 0 !important;
        margin-bottom: -0.5rem !important;
    }

    /* Single view: controls and chart share one slate analysis card.
       Recolour ONLY the child chart section, including its indicator legend. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    :is(.st-key-analysis_a .st-key-chart_a,
        .st-key-analysis_b .st-key-chart_b) {
        background: #0e1117 !important;
        border-top: 0 !important;
        border-radius: 12px !important;
        /* Existing Streamlit vertical gap is about 16px; move the inset
           chart up 8px so the visible controls-to-chart gap is about 8px. */
        margin-top: -8px !important;
        padding: 9px 4px 10px !important;
    }

    /* V16: mobile One gets independent Occupation and Chart cards, like
       Overlay. The page already has 8px side margins; the chart card uses
       the same internal horizontal padding and slate-black palette. */
    .st-key-lme_mobile_one_chart_workspace {
        margin-top: -8px !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    .st-key-lme_mobile_one_chart_workspace .st-key-chart_a {
        background: #0e1117 !important;
        color: var(--lme-preview-foreground) !important;
        border-radius: 14px !important;
        box-shadow: var(--lme-preview-shadow) !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    .st-key-lme_mobile_one_chart_workspace
    [data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-chart_a) {
        background: #0e1117 !important;
        border-color: #35404e !important;
        border-radius: 14px !important;
    }

    /* Overlay: occupation A/B columns stack on phones. Tighten that gap
       and the gap from Occupation B to the separate plot card to ~8px. */
    [data-testid="stHorizontalBlock"]:has(.st-key-controls_a):has(.st-key-controls_b) {
        gap: 8px !important;
    }
    .st-key-lme_overlay_chart_workspace {
        margin-top: -8px !important;
    }

    /* Overlay view: its own chart card contains both line keys and legend. */
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    .st-key-combined_chart {
        background: #0e1117 !important;
    }
    .stMainBlockContainer:has(.st-key-lme_explorer_toolbar)
    [data-testid="stVerticalBlockBorderWrapper"]:has(.st-key-combined_chart) {
        background: #0e1117 !important;
        border-color: #35404e !important;
    }
}
</style>""")


# Mobile Overlay: preserve full labels while making the two line keys compact.
# Desktop positioning and the native chart toolbar remain unchanged.
st.html("""<style>
@media (max-width: 768px) {
    .st-key-combined_chart .lme-overlay-line-keys {
        /* Keep ellipsis on two lines; give 8px more room below labels. */
        padding-right: 38px !important;
        gap: 6px !important;
        margin-bottom: 16px !important;
    }
    .st-key-combined_chart .lme-overlay-line-keys > div {
        gap: 7px !important;
    }
    .st-key-combined_chart .lme-overlay-line-keys span[aria-hidden="true"] {
        flex: 0 0 28px !important;
        width: 28px !important;
    }
    .st-key-combined_chart .lme-overlay-line-keys > div > span:last-child {
        font-size: 15px !important;
        line-height: 1.25 !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
        display: block !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
}
</style>""")


def render_combined_chart(payload_a, payload_b, chart_container) -> None:
    """Draw both independently configured selections on one shared plot."""
    # Two self-contained line keys above the plot replace the repeated A/B
    # explanation and the native Vega stroke-dash legend. Keep A/B internally.
    # Match Overlay legend labels to the qualification selector; do not alter
    # the underlying German BA values or the One/Two chart labels.
    short_qualifications = {
        "Overall": "All", "Helpers": "Helper",
        "Specialists": "Specialist", "Experts": "Expert",
    }

    def overlay_label(payload):
        qualification = payload["qualification_label"]
        qualification = short_qualifications.get(qualification, qualification)
        return f"{payload['display_name']} · {qualification}"

    title_a = overlay_label(payload_a)
    title_b = overlay_label(payload_b)
    safe_a = html.escape(title_a, quote=True)
    safe_b = html.escape(title_b, quote=True)
    chart_container.markdown(
        f"""
        <div class="lme-overlay-line-keys" style="
            display:flex; flex-direction:column; gap:8px;
            padding-right:110px; margin:2px 0 7px; min-width:0;">
          <div style="display:flex;align-items:center;gap:11px;min-width:0;">
            <span aria-hidden="true" style="display:inline-block;flex:0 0 42px;
              width:42px;border-top:3px solid #91b6e2;"></span>
            <span style="font-weight:600;line-height:1.35;overflow-wrap:anywhere;">{safe_a}</span>
          </div>
          <div style="display:flex;align-items:center;gap:11px;min-width:0;">
            <span aria-hidden="true" style="display:inline-block;flex:0 0 42px;
              width:42px;border-top:3px dashed #91b6e2;"></span>
            <span style="font-weight:600;line-height:1.35;overflow-wrap:anywhere;">{safe_b}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    frames = []
    for label, payload in (("A", payload_a), ("B", payload_b)):
        frame = payload["plot_df"].copy()
        if not frame.empty:
            frame["selection"] = label
            frame["occupation_selection"] = (
                overlay_label(payload)
            )
            frames.append(frame)

    if not frames:
        chart_container.info("Choose at least one indicator in the legend below.")
        render_overlay_indicator_legend(chart_container)
        return

    plot_df = pd.concat(frames, ignore_index=True)
    color_scale = alt.Scale(
        domain=["Registered vacancies", "Employed people", "Unemployed people", "Job seekers"],
        range=["#E45756", "#4C78A8", "#F2CF5B", "#59A14F"],
    )
    chart = (
        alt.Chart(plot_df)
        .mark_line()
        .encode(
            x=alt.X("report_date:T", title=None),
            y=alt.Y(
                "value:Q",
                title="Index (start = 100)" if view_mode == "Indexed" else None,
                axis=alt.Axis(
                    format=",.0f" if view_mode == "Indexed" else "~s",
                ),
            ),
            color=alt.Color("indicator:N", scale=color_scale, legend=None),
            strokeDash=alt.StrokeDash(
                "selection:N",
                scale=alt.Scale(domain=["A", "B"], range=[[1, 0], [6, 3]]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("report_date:T", title="Date"),
                alt.Tooltip("occupation_selection:N", title="Selection"),
                alt.Tooltip("indicator:N", title="Indicator"),
                alt.Tooltip("value:Q", title="Index" if view_mode == "Indexed" else "Value",
                            format=",.1f" if view_mode == "Indexed" else ",.0f"),
            ],
        )
        .properties(height=CHART_HEIGHT)
    )
    if ENABLE_CHART_PAN_ZOOM:
        chart = chart.interactive()
    chart_container.altair_chart(chart, width="stretch")
    # One shared set of indicators for both occupation selections.
    render_overlay_indicator_legend(chart_container)


# Equal Qualification button widths only on desktop. Preserve natural widths
# and scrolling on phone-sized displays. These selectors target only the
# qualification segmented controls; no global button styling is changed.
st.html("""<style>
@media (min-width: 1061px) {
    :is(.st-key-controls_a, .st-key-controls_b)
    div[class*="st-key-qualification_tabs_"]
    button[data-variant="segmented_control"] {
        width: 84px !important;
        min-width: 84px !important;
        max-width: 84px !important;
        box-sizing: border-box !important;
        padding-left: 4px !important;
        padding-right: 4px !important;
        flex: 0 0 84px !important;
    }
}
</style>""")


# In desktop Single mode, center the only analysis card and leave room on both
# sides. Below 1061px, keep the native full-width mobile/tablet layout.
st.html("""<style>
@media (min-width: 1061px) {
    .st-key-lme_single_workspace {
        width: 100% !important;
        max-width: 900px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Overlay controls retain exactly the Two layout (full page width).
       Center ONLY the combined chart card, matching the 900px One card. */
    .st-key-lme_overlay_chart_workspace {
        width: 100% !important;
        max-width: 900px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
}
</style>""")

# Controls and chart output adapt to the selected workspace layout.
# Compare and Single: one card per analysis, with a subtle divider between
# the filters and the chart. Keep the child keys for CSS and widget stability.
def make_analysis_card(parent, suffix: str):
    outer = parent.container(border=True, key=f"analysis_{suffix}")
    controls = outer.container(border=False, key=f"controls_{suffix}")
    chart = outer.container(border=False, key=f"chart_{suffix}")
    return controls, chart


if layout_mode == "Compare":
    chart_a_col, chart_b_col = st.columns([1, 1], gap="medium")
    controls_a, chart_a = make_analysis_card(chart_a_col, "a")
    controls_b, chart_b = make_analysis_card(chart_b_col, "b")
    render_chart(1, controls_a, chart_a)
    render_chart(2, controls_b, chart_b)
elif layout_mode == "Combined":
    # Keep the same full-width two-column controls layout as Two.
    # On phones, reduce only the space between the two occupation cards.
    # Desktop keeps the established medium gap.
    mobile_overlay = _lme_viewport_mode in ("portrait", "landscape")
    controls_a_col, controls_b_col = st.columns(
        [1, 1], gap="small" if mobile_overlay else "medium"
    )
    with controls_a_col:
        controls_a = st.container(border=True, key="controls_a")
    with controls_b_col:
        controls_b = st.container(border=True, key="controls_b")
    overlay_chart_workspace = st.container(key="lme_overlay_chart_workspace")
    combined_chart = overlay_chart_workspace.container(border=True, key="combined_chart")
    ensure_overlay_indicators()
    overlay_selection = {
        label: bool(st.session_state[f"overlay_indicator_{label}"])
        for label, _ in INDICATOR_LEGEND
    }
    payload_a = render_chart(1, controls_a, None, render_output=False,
                             indicator_override=overlay_selection)
    payload_b = render_chart(2, controls_b, None, render_output=False,
                             indicator_override=overlay_selection)
    render_combined_chart(payload_a, payload_b, combined_chart)
else:
    # V16 mobile One: same separate control / chart cards as Overlay.
    # Keep the original combined analysis card unchanged on desktop.
    mobile_one = _lme_viewport_mode in ("portrait", "landscape")
    if mobile_one:
        controls_a = st.container(border=True, key="controls_a")
        chart_workspace = st.container(key="lme_mobile_one_chart_workspace")
        chart_a = chart_workspace.container(border=True, key="chart_a")
    else:
        single_workspace = st.container(key="lme_single_workspace")
        controls_a, chart_a = make_analysis_card(single_workspace, "a")
    render_chart(1, controls_a, chart_a)
