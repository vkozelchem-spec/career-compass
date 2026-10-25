"""Responsive LME welcome screen.

Independent from the data-loading/chart logic. The caller owns navigation.
Browser persistence is handled by the app-level preference callback.
"""

from typing import Callable
import html

from lme_i18n import tr

import streamlit as st


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
/* Welcome header: language at the LEFT edge, About at the RIGHT edge.
   Keep the two actions on one line even when Streamlit stacks columns. */
.st-key-lme_welcome_header [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: .35rem !important;
}
.st-key-lme_welcome_header [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
    flex: 0 0 128px !important;
    width: 128px !important;
    min-width: 0 !important;
    max-width: 128px !important;
}
.st-key-lme_welcome_header [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
.st-key-lme_welcome_header [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
/* Language is a quiet text action, matching About at the opposite edge.
   Keep the trigger borderless in both light and dark browser themes. */
.st-key-lme_welcome_language_area [data-testid="stPopover"] button {
    width: auto !important;
    min-width: 0 !important;
    min-height: 36px !important;
    padding: .25rem .1rem !important;
    justify-content: flex-start !important;
    background: transparent !important;
    background-color: transparent !important;
    color: #475467 !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    font-weight: 600 !important;
    color-scheme: light !important;
}
.st-key-lme_welcome_language_area [data-testid="stPopover"] button :is(p, span, svg) {
    color: #475467 !important;
    -webkit-text-fill-color: #475467 !important;
}
.st-key-lme_welcome_language_area [data-testid="stPopover"] button:hover {
    background: transparent !important;
    color: #171717 !important;
}
.st-key-lme_welcome_language_area [data-testid="stPopover"] button:focus:not(:focus-visible) {
    outline: none !important;
    box-shadow: none !important;
}
.st-key-lme_welcome_language_area [data-testid="stPopover"] button:focus-visible {
    outline: 2px solid #8093aa !important;
    outline-offset: 2px !important;
}
/* The language popover is portaled to the page body by Streamlit.
   Use its unique marker to avoid affecting Explorer or About popovers. */
body [data-baseweb="popover"]:has(.lme-welcome-language-popup-marker),
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker) {
    color-scheme: light !important;
    background: #fff !important;
    background-color: #fff !important;
    color: #27303f !important;
    border: 1px solid #d5d9df !important;
    border-radius: 10px !important;
    box-shadow: 0 7px 20px rgba(16, 24, 40, .12) !important;
}
/* Give the popup an EXPLICIT compact width, on both mobile and desktop.
   100% here expanded the popover to the whole desktop viewport: the outer
   BaseWeb overlay can itself be full-width, so percentage sizing is unsafe. */
body [data-baseweb="popover"]:has(.lme-welcome-language-popup-marker),
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker) {
    width: min(210px, calc(100vw - 32px)) !important;
    min-width: 0 !important;
    max-width: min(210px, calc(100vw - 32px)) !important;
    box-sizing: border-box !important;
}
body [data-baseweb="popover"]:has(.lme-welcome-language-popup-marker) > div {
    width: 100% !important;
    min-width: 0 !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker) {
    /* Compact top and bottom spacing around the two options. */
    padding: .2rem .3rem !important;
}
/* Reset theme-painted nested portal wrappers without touching the two buttons. */
body [data-baseweb="popover"]:has(.lme-welcome-language-popup-marker)
:is(div, ul, li, p, span, label):not([data-testid="stPopoverBody"]) {
    background-color: transparent !important;
    color: #27303f !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
:is([data-testid="stVerticalBlock"], [data-testid="stElementContainer"],
    [data-testid="stButton"], [data-testid="stMarkdownContainer"]) {
    background: transparent !important;
    color: #27303f !important;
    box-shadow: none !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[data-testid="stElementContainer"]:has(.lme-welcome-language-popup-marker) {
    display: none !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[data-testid="stVerticalBlock"] {
    gap: .1rem !important;
    padding: 0 !important;
    margin: 0 !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[class*="st-key-lme_welcome_language_option_"] button {
    display: flex !important;
    justify-content: flex-start !important;
    width: 100% !important;
    min-height: 32px !important;
    padding: .2rem .55rem !important;
    text-align: left !important;
    background: #fff !important;
    color: #27303f !important;
    border: none !important;
    border-radius: 7px !important;
    box-shadow: none !important;
    font-weight: 500 !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[class*="st-key-lme_welcome_language_option_"] button :is(p, span) {
    background: transparent !important;
    color: #27303f !important;
    -webkit-text-fill-color: #27303f !important;
    text-align: left !important;
}
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[class*="st-key-lme_welcome_language_option_"] button:is([kind="primary"], [data-testid="stBaseButton-primary"]),
body [data-testid="stPopoverBody"]:has(.lme-welcome-language-popup-marker)
[class*="st-key-lme_welcome_language_option_"] button:hover {
    background: #e9ebef !important;
    color: #171717 !important;
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
/* Full-width CTA on both desktop and mobile. */
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
/* On desktop the secondary preference sits ABOVE the primary CTA.
   There is still only one checkbox and one persistent widget key.
   Reverse only the Streamlit vertical block containing BOTH action elements. */
@media (min-width: 769px) {
    .lme-welcome-grid {
        /* Without the LME emblem, let the headline start immediately below About. */
        margin-top: 0;
        margin-bottom: .4rem;
    }
    .st-key-lme_welcome_actions[data-testid="stVerticalBlock"]:has(.st-key-lme_welcome_explore):has(.st-key-lme_welcome_skip_area),
    .st-key-lme_welcome_actions [data-testid="stVerticalBlock"]:has(.st-key-lme_welcome_explore):has(.st-key-lme_welcome_skip_area) {
        display: flex !important;
        flex-direction: column-reverse !important;
    }
    .st-key-lme_welcome_skip_area {
        padding-top: 0;
        padding-bottom: .35rem;
    }
}
/* Larger, more readable feature list on desktop; mobile stays unchanged. */
@media (min-width: 1024px) {
    .lme-welcome-benefit {
        font-size: clamp(1.125rem, 1.15vw, 1.25rem);
        line-height: 1.45;
        margin-bottom: 1.2rem;
        gap: .85rem;
    }
    .lme-welcome-dot {
        flex: 0 0 9px;
        width: 9px;
        height: 9px;
        margin-top: .58em;
        margin-right: .45rem;
    }
}
@media (max-width: 768px) {
    .lme-welcome-grid {
        grid-template-columns: minmax(0, 1fr);
        grid-template-areas: "heading" "graph" "benefits";
        /* Bring the headline close to the minimal About link. */
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
    <h1 class="lme-welcome-headline">{headline}</h1>
  </div>
  <div class="lme-welcome-graph">
    <div class="lme-welcome-preview">
      <svg viewBox="0 0 420 260" role="img"
        aria-label="{graph_aria}"
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
        <text x="10" y="253" font-size="12" fill="#98a2b3">{graph_caption}</text>
      </svg>
    </div>
  </div>
  <div class="lme-welcome-benefits">
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>{benefit_1}</span></div>
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>{benefit_2}</span></div>
    <div class="lme-welcome-benefit"><span class="lme-welcome-dot" aria-hidden="true"></span>
      <span>{benefit_3}</span></div>
  </div>
</div>
"""


def render_welcome(
    on_explore: Callable[[], None],
    on_about: Callable[[], None],
    skip_default: bool = False,
    on_skip_change: Callable[[], None] | None = None,
    language: str = "En",
) -> bool:
    """Render Welcome, keeping the checkbox in sync with the saved preference."""
    st.markdown(_WELCOME_STYLE, unsafe_allow_html=True)

    # Streamlit removes widget state when an element is not rendered, e.g. while
    # Explorer is visible. Restore it from the app-level preference on return.
    if "lme_skip_welcome" not in st.session_state:
        st.session_state.lme_skip_welcome = skip_default

    # The app supplies the semantic language from session state. Do not attach
    # a selectbox widget key here: Streamlit removes hidden widget keys during
    # navigation, while app.py preserves the preference separately.
    lang = language if language in ("En", "De") else "En"

    def set_welcome_language(selected: str) -> None:
        st.session_state.lme_language = selected
        st.session_state.lme_language_preference = selected
        st.rerun()

    # Left: compact language dropdown. Right: "About" on both EN and DE pages.
    # st.popover replaces native st.selectbox, whose closed field stayed dark
    # on some phone themes despite targeted CSS overrides.
    with st.container(key="lme_welcome_header"):
        language_col, _, about_col = st.columns(
            [1.5, 5, 1], gap="small", vertical_alignment="center"
        )
        with language_col:
            with st.container(key="lme_welcome_language_area"):
                with st.popover(
                    "English" if lang == "En" else "Deutsch",
                    help="More languages (Ru, Ua, Fr) are planned.",
                    width="content",
                ):
                    st.html('<span class="lme-welcome-language-popup-marker" aria-hidden="true"></span>')
                    for code, name in (("En", "English"), ("De", "Deutsch")):
                        if st.button(
                            f"{'✓ ' if code == lang else ''}{name}",
                            key=f"lme_welcome_language_option_{code}",
                            type="primary" if code == lang else "tertiary",
                            width="stretch",
                        ):
                            set_welcome_language(code)
        with about_col:
            if st.button("About ↗", key="lme_welcome_about"):
                on_about()

    content = _WELCOME_CONTENT.format(
        headline=html.escape(tr("Explore the labour market.", lang)).replace("|", "<br>")
        if lang == "De" else "Explore the<br>labour market.",
        graph_aria=html.escape(tr("Illustrative trend lines, not real statistics", lang), quote=True),
        graph_caption=html.escape(tr("Illustrative preview · Germany", lang)),
        benefit_1=html.escape(tr("Browse hundreds of occupations", lang)),
        benefit_2=html.escape(tr("Compare employment and vacancies", lang)),
        benefit_3=html.escape(tr("Understand changes over time", lang)),
    )
    st.markdown(content, unsafe_allow_html=True)

    with st.container(key="lme_welcome_actions"):
        if st.button(f"{tr('Start exploring', lang)} →", key="lme_welcome_explore", width="stretch"):
            on_explore()
        with st.container(key="lme_welcome_skip_area"):
            skip = st.checkbox(
                tr("Don't show this again", lang),
                key="lme_skip_welcome",
                on_change=on_skip_change,
            )

    return skip
