"""Responsive LME welcome screen.

Independent from the data-loading/chart logic. The caller owns navigation.
Browser persistence is handled by the app-level preference callback.
"""

from typing import Callable

import streamlit as st
from lme_brand import COMPASS_SVG


_WELCOME_STYLE = """
<style>
/* Welcome Page: isolated design, no changes to Explorer controls. */
.lme-welcome-grid {
    display: grid;
    grid-template-columns: minmax(0, .92fr) minmax(0, 1.15fr);
    grid-template-areas: "heading graph" "benefits graph";
    column-gap: clamp(1.5rem, 4vw, 4rem);
    row-gap: 1.4rem;
    align-items: center;
    max-width: 1450px;
    margin: clamp(1.6rem, 4vh, 3rem) auto 1.3rem;
}
.lme-welcome-heading { grid-area: heading; align-self: end; }
.lme-welcome-graph { grid-area: graph; min-width: 0; }
.lme-welcome-benefits { grid-area: benefits; align-self: start; }
.lme-welcome-headline {
    margin: 0;
    font-size: clamp(2.2rem, 3.4vw, 3.5rem);
    line-height: 1.11;
    font-weight: 750;
    letter-spacing: -.035em;
    color: #171717;
}
.lme-welcome-preview {
    background: #fff;
    border: 1px solid #e2e5e9;
    border-radius: 18px;
    padding: 1.1rem 1rem .5rem;
    box-shadow: 0 4px 18px rgba(16, 24, 40, .05);
}
.lme-welcome-preview svg { display: block; width: 100%; height: auto; }
.lme-welcome-benefit {
    display: flex;
    align-items: flex-start;
    gap: .75rem;
    margin: 0 0 1rem;
    font-size: .98rem;
    line-height: 1.4;
    color: #27303f;
}
.lme-welcome-dot {
    flex: 0 0 7px;
    width: 7px;
    height: 7px;
    margin: .4em .5rem 0 .3rem;
    background: #e30613;
    border-radius: 50%;
}
.lme-welcome-brand {
    display: flex;
    align-items: center;
    gap: .55rem;
    color: #171717;
    font-size: 1.13rem;
    font-weight: 700;
    white-space: nowrap;
}
.lme-welcome-brand-icon { display: inline-flex; align-items: center; }
.lme-welcome-brand-icon svg { width: 20px; height: 20px; }
/* Streamlit columns normally stack on phones. Only this header stays in a row. */
.st-key-lme_welcome_header div[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: .35rem !important;
}
.st-key-lme_welcome_header div[data-testid="stColumn"]:first-child {
    flex: 1 1 0 !important;
    width: auto !important;
    min-width: 0 !important;
}
.st-key-lme_welcome_header div[data-testid="stColumn"]:last-child {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
/* 'About' is a light navigation link, not a full-width CTA. */
.st-key-lme_welcome_about button {
    width: auto !important;
    min-height: 2rem !important;
    padding: .25rem .5rem !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: #475467 !important;
    font-weight: 600 !important;
}
.st-key-lme_welcome_about button:hover {
    background: #e9ebef !important;
    color: #171717 !important;
}
/* Bounded CTA on desktop, full width on mobile. */
.st-key-lme_welcome_explore { max-width: none; }
.st-key-lme_welcome_explore button {
    background: #e30613 !important;
    color: #fff !important;
    border-color: #e30613 !important;
    min-height: 3.15rem !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
}
.st-key-lme_welcome_explore button:hover {
    background: #c90011 !important;
    border-color: #c90011 !important;
    color: #fff !important;
}
.st-key-lme_welcome_actions { max-width: 1450px; margin: 0 auto; }
/* The persistent preference is secondary: keep it below the primary CTA. */
.st-key-lme_welcome_skip_area {
    padding-top: .45rem;
    padding-bottom: 1rem;
}
@media (max-width: 768px) {
    .lme-welcome-grid {
        grid-template-columns: minmax(0, 1fr);
        grid-template-areas: "heading" "graph" "benefits";
        /* Keep comfortable separation from the LME/About header,
           while reducing the space between the headline and preview. */
        row-gap: .5rem;
        margin-top: -1.15rem;
        margin-bottom: .1rem;
    }
    .lme-welcome-heading, .lme-welcome-benefits { align-self: auto; }
    /* Fine-tune only the mobile composition. Desktop stays untouched. */
    .lme-welcome-graph { margin-top: -.55rem; }
    .lme-welcome-headline { font-size: clamp(2rem, 8.4vw, 2.5rem); }
    .lme-welcome-preview { padding: .65rem .55rem .3rem; border-radius: 16px; }
    .lme-welcome-benefit { font-size: .92rem; margin-bottom: .68rem; }
    .st-key-lme_welcome_explore { max-width: none; }
    /* Keep the lower-right Streamlit hosting badge away from the checkbox. */
    .st-key-lme_welcome_skip_area {
        padding-right: 5.5rem;
        padding-bottom: max(4.5rem, env(safe-area-inset-bottom));
    }
}
</style>
"""


_WELCOME_CONTENT = """
<div class="lme-welcome-grid">
  <div class="lme-welcome-heading">
    <h1 class="lme-welcome-headline">Explore the<br>labour market.</h1>
  </div>
  <div class="lme-welcome-graph">
    <div class="lme-welcome-preview">
      <svg viewBox="0 0 420 260" role="img"
        aria-label="Illustrative trend lines, not real statistics"
        xmlns="http://www.w3.org/2000/svg">
        <g stroke="#e6e8eb" stroke-width="1">
          <path d="M8 45H412 M8 95H412 M8 145H412 M8 195H412"/>
        </g>
        <path d="M8 165 C60 171 85 115 135 135 S200 194 245 120 S340 120 412 30"
          fill="none" stroke="#e30613" stroke-width="4" stroke-linecap="round"/>
        <path d="M8 199 C76 167 105 200 155 164 S231 161 285 119 S358 154 412 110"
          fill="none" stroke="#4c78a8" stroke-width="4" stroke-linecap="round"/>
        <path d="M8 230 C65 227 108 214 160 210 S236 197 297 211 S364 173 412 179"
          fill="none" stroke="#59a14f" stroke-width="3.5" stroke-linecap="round"/>
        <text x="10" y="253" font-size="12" fill="#98a2b3">Illustrative preview · Germany</text>
      </svg>
    </div>
  </div>
  <div class="lme-welcome-benefits">
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>Browse hundreds of occupations</span></div>
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>Compare employment and vacancies</span></div>
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>Understand changes over time</span></div>
  </div>
</div>
"""


def render_welcome(
    on_explore: Callable[[], None],
    on_about: Callable[[], None],
    skip_default: bool = False,
    on_skip_change: Callable[[], None] | None = None,
) -> bool:
    """Render Welcome, keeping the checkbox in sync with the saved preference."""
    st.markdown(_WELCOME_STYLE, unsafe_allow_html=True)

    # Streamlit removes widget state when an element is not rendered, e.g. while
    # Explorer is visible. Restore it from the app-level preference on return.
    if "lme_skip_welcome" not in st.session_state:
        st.session_state.lme_skip_welcome = skip_default

    with st.container(key="lme_welcome_header"):
        brand_col, about_col = st.columns([5, 1], vertical_alignment="center")
        with brand_col:
            st.markdown(
                '<div class="lme-welcome-brand">'
                f'<span class="lme-welcome-brand-icon">{COMPASS_SVG}</span>'
                '<span>LME</span></div>',
                unsafe_allow_html=True,
            )
        with about_col:
            if st.button("About ↗", key="lme_welcome_about"):
                on_about()

    st.markdown(_WELCOME_CONTENT, unsafe_allow_html=True)

    with st.container(key="lme_welcome_actions"):
        if st.button("Start exploring →", key="lme_welcome_explore", width="stretch"):
            on_explore()
        with st.container(key="lme_welcome_skip_area"):
            skip = st.checkbox(
                "Don't show this again",
                key="lme_skip_welcome",
                on_change=on_skip_change,
            )

    return skip
