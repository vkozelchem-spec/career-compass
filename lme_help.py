"""Mobile-first, EN/DE How it works page for Career Compass / LME.

Only the plots and occupation panel are raster crops from real Explorer
screenshots supplied for the guide. Layout, copy, navigation and KldB tree
are HTML/CSS, so they can be refined without regenerating a full-page image.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Callable

import streamlit as st

from lme_i18n import tr
from lme_brand import lme_home_button_style

_ASSETS = Path(__file__).parent / "assets"


_HELP_CSS = """
<style>
/* Scopes styles to Help. The Explorer's chart and toolbar styles stay intact. */
.lme-help-root {
    --help-navy: #344559;
    --help-dark: #0e1117;
    --help-text: #203049;
    --help-blue: #4c78a8;
    --help-yellow: #e9c350;
    max-width: 430px;
    margin: 0 auto;
    padding: .2rem 0 .75rem;
    font-family: inherit;
    color: var(--help-text);
}
.lme-help-root * { box-sizing: border-box; }
.lme-help-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    background: var(--help-navy);
    color: #fff;
    border-radius: 15px;
    padding: 1rem 1.05rem;
    margin: 0 0 .7rem;
}
.lme-help-hero h1 {
    color: #fff !important;
    font-size: clamp(1.6rem, 6vw, 2rem);
    line-height: 1.14;
    letter-spacing: normal;
    font-weight: 700;
    margin: 0 0 .3rem;
}
.lme-help-hero p { margin: 0; color: #e2e9f3; font-size: .88rem; line-height: 1.4; }
.lme-help-hero-icon {
    width: 55px;
    height: 55px;
    border: 1px solid #91a9c3;
    background: #435d7c;
    border-radius: 12px;
    display: grid;
    place-items: center;
    flex: 0 0 auto;
}
.lme-help-step {
    background: #f8fafd;
    border: 1px solid #e1e6ed;
    border-radius: 16px;
    padding: .85rem .78rem .85rem;
    margin-bottom: .7rem;
    box-shadow: 0 2px 9px rgba(32,48,73,.035);
}
.lme-help-heading { display: flex; align-items: center; gap: .55rem; margin: 0 0 .45rem; }
.lme-help-number {
    width: 31px; height: 31px; flex: 0 0 31px;
    display: grid; place-items: center; border-radius: 50%;
    background: #237bd9; color: #fff; font-size: 1.06rem; font-weight: 700;
}
.lme-help-heading h2 {
    color: #111b2b !important;
    font-size: 1.14rem;
    letter-spacing: normal;
    line-height: 1.25;
    font-weight: 700;
    margin: 0;
}
.lme-help-description { color: #4b5e78; font-size: .87rem; line-height: 1.46; margin: .1rem 0 .65rem; }
.lme-help-panel-shot { position: relative; margin: 0 0 .55rem; }
.lme-help-panel-shot img { width: 100%; height: auto; border-radius: 10px; display: block; }
.lme-help-pin {
    position: absolute; display: grid; place-items: center;
    width: 21px; height: 21px; border: 2px solid #fff;
    border-radius: 50%; background: #237bd9; color: #fff;
    font: 700 11px/1 sans-serif; box-shadow: 0 1px 4px #12243a55;
}
.lme-help-pin.search { left: 52%; top: 49%; }
.lme-help-pin.tree { left: 98%; top: 47%; transform: translate(-50%, -50%); }
.lme-help-pin.back { left: 92%; top: 12%; }
.lme-help-pin.qual { left: 17%; top: 84%; }
.lme-help-notes { display: grid; grid-template-columns: 1fr 1fr; gap: .35rem .55rem; margin: .55rem 0 .75rem; }
.lme-help-note { display:flex; align-items:baseline; gap:.3rem; font-size:.75rem; color: #42546f; line-height:1.28; }
.lme-help-note b { color: #237bd9; min-width: .75rem; }
.lme-help-tree { background:#eff4fa; padding: .7rem; border-radius: 12px; }
.lme-help-tree-label { font-size: .74rem; font-weight: 700; color:#40536b; margin:0 0 .45rem; }
.lme-help-tree-path {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: .3rem;
    padding-left: .65rem;
}
.lme-help-tree-path::before {
    content: "";
    position: absolute;
    left: .18rem;
    top: .5rem;
    bottom: .6rem;
    width: 2px;
    background: #c1d1e4;
}
.lme-help-tree-root {
    color: #435a78;
    font-size: .75rem;
    font-weight: 600;
    padding: .1rem 0 .1rem .2rem;
}
.lme-help-tree-level {
    display: grid;
    grid-template-columns: 43px minmax(0, 1fr);
    align-items: start;
    gap: .42rem;
    padding: .2rem .35rem;
    background: rgba(255,255,255,.64);
    border: 1px solid #e0e8f3;
    border-radius: 7px;
    color: #304762;
    font-size: .73rem;
    line-height: 1.34;
}
.lme-help-tree-code {
    display: inline-block;
    font-size: .73rem;
    font-weight: 700;
    color: #2f608b;
    font-variant-numeric: tabular-nums;
}
.lme-help-tree-level:last-child {
    border-color: #b4cbe2;
    background: #e3edf8;
}
.lme-help-tree-example {
    display: block;
    margin: .38rem 0 .1rem .75rem;
    font-size: .7rem;
    color: #53667f;
}
.lme-help-tree-foot { color:#53667f; font-size:.73rem; line-height:1.4; margin:.48rem 0 0; }
.lme-help-chart {
    border-radius: 11px;
    background: var(--help-dark);
    color: #f7f9fc;
    overflow: hidden;
    padding: .72rem .45rem .35rem;
}
.lme-help-chart-header { padding: 0 .35rem .3rem; }
.lme-help-series { display: flex; align-items: flex-start; gap:.45rem; font-size:.77rem; font-weight:600; line-height:1.35; margin:.1rem 0; }
.lme-help-stroke { height:0; width:22px; flex:0 0 22px; margin-top:.49rem; border-top:3px solid #8eb7e5; }
.lme-help-stroke.dashed { border-top-style:dashed; }
.lme-help-chart img { display:block; width: 100%; height:auto; }
.lme-help-chart-foot { display:flex; gap:.7rem; padding: 0 .4rem .25rem; font-size:.67rem; color:#b8c7da; }
.lme-help-chart-foot span::before { content: '●'; color: #7dadde; margin-right:.23rem; }
.lme-help-chart-foot span:last-child::before { color: var(--help-yellow); }
.lme-help-inline-control { display:flex; align-items:center; justify-content:flex-end; gap:.42rem; margin: -.15rem 0 .5rem; }
.lme-help-inline-control .mode {
    font-size:.75rem; font-weight:600; padding:.23rem .5rem;
    border-radius:6px; color:#344559; background:#e8edf4;
}
.lme-help-inline-control .mode.active { background:#237bd9; color:#fff; }
.lme-help-inline-control .label { color:#51637b; font-size:.73rem; }
.lme-help-mobile-compare { width:27px; height:27px; background:#435d7c; border-radius:7px; display:grid; place-items:center; }
.lme-help-mobile-compare img { width:23px; height:23px; object-fit:contain; display:block; }
.lme-help-hero-icon img { width:31px; height:31px; object-fit: contain; display:block; }
.lme-help-takeaway { font-size:.79rem; color:#4a5d77; line-height:1.43; margin:.5rem 0 0; }
@media (max-width: 520px) {
    .stMainBlockContainer:has(.lme-help-root) {
        padding: .7rem .7rem 1.25rem !important;
    }
    .lme-help-root { width:100%; }
    .lme-help-step { padding:.8rem .6rem; }
    .lme-help-hero { padding: .9rem .85rem; }
    .lme-help-hero-icon { width:47px; height:47px; }
    .lme-help-notes { gap: .3rem .4rem; }
}
.st-key-lme_help_nav, .st-key-lme_help_actions {
    max-width:430px;
    margin:0 auto;
}
/* Keep the familiar Explorer Home icon and Back on one row, even on phones. */
.st-key-lme_help_nav [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: .4rem !important;
}
.st-key-lme_help_nav [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
}
.st-key-lme_help_nav .st-key-lme_help_back button {
    border: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
    color: #475467 !important;
    font-size: .88rem !important;
    white-space: nowrap;
    padding: .25rem .35rem !important;
}
.stMainBlockContainer:has(.lme-help-root) {
    padding-top: .5rem !important;
}
.st-key-lme_help_actions button {
    min-height: 44px !important;
    background: #e30613 !important; color: #fff !important;
    border: 1px solid #e30613 !important;
    font-weight: 700 !important; border-radius:10px !important;
}
.st-key-lme_help_actions button:hover { background:#c90011 !important; border-color:#c90011 !important; }
</style>
"""


def _image_uri(filename: str) -> str:
    """Embed a small, fixed screenshot crop in the single HTML guide."""
    path = _ASSETS / filename
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _text(english: str, lang: str) -> str:
    return html.escape(tr(english, lang), quote=True)


def render_help(
    on_explore: Callable[[], None],
    on_welcome: Callable[[], None],
    language: str = "En",
    from_welcome: bool = False,
) -> None:
    """Render scrolling Help without loading any Explorer datasets."""
    lang = language if language in ("En", "De") else "En"
    t = lambda english: _text(english, lang)
    st.markdown(_HELP_CSS, unsafe_allow_html=True)

    # Reuse the exact Home button styling and widget key from Explorer.
    # Only one of Explorer and Help renders on a given run.
    st.markdown(lme_home_button_style(), unsafe_allow_html=True)
    with st.container(key="lme_help_nav"):
        home_col, back_col = st.columns([1, 1], vertical_alignment="center", gap="small")
        with home_col:
            if st.button(tr("Home", lang), key="lme_explorer_home", type="tertiary",
                         help=tr("Back to Welcome", lang), width="content"):
                on_welcome()
        with back_col:
            if st.button(t("← Back"), key="lme_help_back", type="tertiary", width="content"):
                (on_welcome if from_welcome else on_explore)()

    panel = _image_uri("help_occupation.jpg")
    one = _image_uri("help_one_plot.jpg")
    overlay = _image_uri("help_overlay_plot.jpg")
    indexed = _image_uri("help_indexed_plot.jpg")
    map_icon = "data:image/png;base64," + base64.b64encode((_ASSETS / "help_map_icon.png").read_bytes()).decode("ascii")
    compare_icon = "data:image/png;base64," + base64.b64encode((_ASSETS / "help_compare_icon.png").read_bytes()).decode("ascii")

    markup = f"""
    <section class="lme-help-root" aria-label="{t('How it works')}">
      <header class="lme-help-hero">
        <div><h1>{t('How it works')}</h1>
        <p>{t('A quick guide to exploring occupations and labour market trends.')}</p></div>
        <div class="lme-help-hero-icon" aria-hidden="true">
          <img src="{map_icon}" alt="" />
        </div>
      </header>
      <article class="lme-help-step">
        <div class="lme-help-heading"><span class="lme-help-number">1</span><h2>{t('Choose an occupation')}</h2></div>
        <p class="lme-help-description">{t('Search by name or browse the KldB categories. Choose a qualification level if needed.')}</p>
        <figure class="lme-help-panel-shot">
          <img src="{panel}" alt="{t('Occupation selection panel with category button and qualification choices')}" />
          <span class="lme-help-pin search" aria-hidden="true">1</span>
          <span class="lme-help-pin tree" aria-hidden="true">2</span>
          <span class="lme-help-pin back" aria-hidden="true">3</span>
          <span class="lme-help-pin qual" aria-hidden="true">4</span>
        </figure>
        <div class="lme-help-notes">
          <div class="lme-help-note"><b>1</b><span>{t('Select or search by name')}</span></div>
          <div class="lme-help-note"><b>2</b><span>{t('Browse the classification tree')}</span></div>
          <div class="lme-help-note"><b>3</b><span>{t('Return one level')}</span></div>
          <div class="lme-help-note"><b>4</b><span>{t('Select qualification')}</span></div>
        </div>
        <div class="lme-help-tree">
          <p class="lme-help-tree-label">{t('KldB hierarchy — a real example')}</p>
          <div class="lme-help-tree-path">
            <div class="lme-help-tree-root">{t('All occupations')}</div>
            <div class="lme-help-tree-level"><span class="lme-help-tree-code">4</span><span>{t('Natural sciences, geography and IT')}</span></div>
            <div class="lme-help-tree-level"><span class="lme-help-tree-code">41</span><span>{t('Mathematics, biology, chemistry and physics')}</span></div>
            <div class="lme-help-tree-level"><span class="lme-help-tree-code">413</span><span>{t('Chemistry')}</span></div>
            <div class="lme-help-tree-level"><span class="lme-help-tree-code">4131</span><span>{t('Chemical and pharmaceutical technology')}</span></div>
            <div class="lme-help-tree-level"><span class="lme-help-tree-code">41312</span><span>{t('Chemical and pharmaceutical technology — Skilled')}</span></div>
          </div>
          <span class="lme-help-tree-example">{t('Example occupation: chemical plant operator (Chemikant/in)')}</span>
          <p class="lme-help-tree-foot">{t('The five KldB levels narrow the field; the final digit indicates qualification. You can select a broader group, too.')}</p>
        </div>
      </article>
      <article class="lme-help-step">
        <div class="lme-help-heading"><span class="lme-help-number">2</span><h2>{t('One chart')}</h2></div>
        <p class="lme-help-description">{t('One shows how a single occupation changes over time. You can show or hide indicators below the chart.')}</p>
        <div class="lme-help-chart" role="group" aria-label="{t('Real chart: Software development and programming')}">
          <div class="lme-help-chart-header"><div class="lme-help-series">{t('Software development and programming')}</div></div>
          <img src="{one}" alt="{t('Real absolute-values plot of software development and programming, with employed and unemployed series')}" />
          <div class="lme-help-chart-foot"><span>{t('Employed')}</span><span>{t('Unemployed')}</span></div>
        </div>
      </article>
      <article class="lme-help-step">
        <div class="lme-help-heading"><span class="lme-help-number">3</span><h2>{t('Overlay')}</h2></div>
        <p class="lme-help-description">{t('Overlay compares two occupations on one chart. Tap the comparison icon to open a second selection panel.')}</p>
        <div class="lme-help-inline-control"><div class="lme-help-mobile-compare" aria-hidden="true">
            <img src="{compare_icon}" alt="" />
          </div><span class="label">{t('Compare occupations')}</span></div>
        <div class="lme-help-chart" role="group" aria-label="{t('Real overlay chart comparing chemistry with software development and programming')}">
          <div class="lme-help-chart-header">
            <div class="lme-help-series"><span class="lme-help-stroke"></span><span>{t('Chemistry')}</span></div>
            <div class="lme-help-series"><span class="lme-help-stroke dashed"></span><span>{t('Software development and programming')}</span></div>
          </div>
          <img src="{overlay}" alt="{t('Real absolute-values overlay plot with solid chemistry lines and dashed software-development lines')}" />
          <div class="lme-help-chart-foot"><span>{t('Employed')}</span><span>{t('Unemployed')}</span></div>
        </div>
        <p class="lme-help-takeaway">{t('Solid lines show the first occupation; dashed lines show the second.')}</p>
      </article>
      <article class="lme-help-step">
        <div class="lme-help-heading"><span class="lme-help-number">4</span><h2>{t('Indexed mode')}</h2></div>
        <p class="lme-help-description">{t('Switch from Abs to Idx to compare relative changes. Each series starts at 100; index values are not percentages.')}</p>
        <div class="lme-help-inline-control"><span class="mode">Abs</span><span class="mode active">Idx</span></div>
        <div class="lme-help-chart" role="group" aria-label="{t('Real indexed plot of chemistry and software development')}">
          <div class="lme-help-chart-header">
            <div class="lme-help-series"><span class="lme-help-stroke"></span><span>{t('Chemistry')}</span></div>
            <div class="lme-help-series"><span class="lme-help-stroke dashed"></span><span>{t('Software development and programming')}</span></div>
          </div>
          <img src="{indexed}" alt="{t('Real indexed chart with employed and unemployed series starting at 100')}" />
          <div class="lme-help-chart-foot"><span>{t('Employed')}</span><span>{t('Unemployed')}</span></div>
        </div>
      </article>
    </section>
    """
    st.html(markup)

    with st.container(key="lme_help_actions"):
        if st.button(f"{t('Back to Explorer' if not from_welcome else 'Start exploring')} →",
                     key="lme_help_explore", width="stretch"):
            on_explore()
