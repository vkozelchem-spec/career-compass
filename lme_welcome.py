"""LME welcome screen, first UI iteration.

The welcome page is intentionally independent of the data loading and chart code.
The caller controls navigation via on_explore and on_about callbacks.
"""

from html import escape
from pathlib import Path
from typing import Callable

import streamlit as st


_ASSETS = Path(__file__).parent / "assets"


def render_welcome(on_explore: Callable[[], None], on_about: Callable[[], None]) -> bool:
    """Render the responsive welcome screen.

    Returns the current checkbox value. Permanent persistence of that
    preference is deliberately postponed until navigation is wired up.
    """
    st.markdown(
        """
        <style>
        .lme-welcome-shell {max-width: 1040px; margin: 0 auto;}
        .lme-welcome-kicker {font-size: .74rem; letter-spacing: .13em;
            font-weight: 750; color: #667085; margin: 0 0 .65rem;}
        .lme-welcome-headline {font-size: clamp(2rem, 4.5vw, 3.7rem);
            line-height: 1.08; font-weight: 750; letter-spacing: -.04em;
            color: #171717; margin: 0 0 1.3rem;}
        .lme-welcome-preview {background: #fff; border: 1px solid #e2e5e9;
            border-radius: 18px; padding: 1rem 1rem .6rem;
            box-shadow: 0 4px 18px rgba(16,24,40,.05);}
        .lme-welcome-benefit {display: flex; align-items: center;
            gap: .7rem; margin: .7rem 0; color: #27303f;
            font-size: .98rem;}
        .lme-welcome-dot {flex: 0 0 21px; color: #e30613;
            font-weight: 800; font-size: 1.1rem;}
        .lme-welcome-footnote {color: #98a2b3; font-size: .75rem;}
        [class*="st-key-lme_welcome_explore"] button {
            background: #e30613 !important; color: white !important;
            border-color: #e30613 !important; min-height: 3.15rem;
            font-weight: 700 !important; border-radius: 10px !important;
        }
        [class*="st-key-lme_welcome_explore"] button:hover {
            background: #c90011 !important; border-color: #c90011 !important;
            color: white !important;
        }
        @media (max-width: 768px) {
          .lme-welcome-shell {padding: 0 .15rem;}
          .lme-welcome-headline {font-size: 2.25rem;}
          .lme-welcome-preview {padding: .75rem .6rem .4rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([4, 1], vertical_alignment="center")
    with top_left:
        st.markdown("#### 🧭 LME")
    with top_right:
        if st.button("About ↗", key="lme_welcome_about", width="stretch"):
            on_about()

    st.write("")
    copy, graph = st.columns([1, 1.15], gap="large", vertical_alignment="center")
    with copy:
        st.markdown(
            '<div class="lme-welcome-kicker">LABOUR MARKET EXPLORER</div>'
            '<div class="lme-welcome-headline">Understand the<br>labour market.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="lme-welcome-benefit"><span class="lme-welcome-dot">✓</span>'
            'Explore hundreds of occupations</div>'
            '<div class="lme-welcome-benefit"><span class="lme-welcome-dot">✓</span>'
            'Compare employment and vacancies</div>'
            '<div class="lme-welcome-benefit"><span class="lme-welcome-dot">✓</span>'
            'Understand changes over time</div>',
            unsafe_allow_html=True,
        )
    with graph:
        st.markdown(
            '''<div class="lme-welcome-preview">
            <svg viewBox="0 0 420 260" role="img"
              aria-label="Illustrative trend lines, not real statistics"
              xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block">
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
            </svg></div>''',
            unsafe_allow_html=True,
        )

    st.write("")
    st.divider()
    skip = st.checkbox("Don't show this again", key="lme_skip_welcome", value=False)
    if st.button("Explore labour market →", key="lme_welcome_explore", width="stretch"):
        on_explore()
    st.caption("Labour Market Explorer · Historical labour market data")
    return skip
