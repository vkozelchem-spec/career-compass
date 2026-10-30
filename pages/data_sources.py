import streamlit as st
from pathlib import Path

from ui import apply_app_style, render_header
#from datetime import date

DATA_DIR = Path(__file__).parent.parent / "data"


labour_parquet = DATA_DIR / "german_labour_market_full.parquet"
employment_parquet = DATA_DIR / "employed_people_full_kldb.parquet"


def render_labour_market_grid():
    start_year = 2011
    end_year = 2026

    html = """
    <div class="coverage-wrap">
        <div class="coverage-grid labour-grid">
    """

    # Top-left empty cell
    html += '<div class="level-header">KldB</div>'

    # Year labels
    for year in range(start_year, end_year + 1):
        html += f'<div class="year-label">{year}</div>'

    # Five KldB levels
    for level in range(1, 6):
        html += f'<div class="level-label">{level}-digit</div>'

        for year in range(start_year, end_year + 1):
            html += '<div class="year-block">'

            for month in range(1, 13):

                # Source starts in July 2011
                source_available = not (
                    year == 2011 and month < 7
                )

                # Source currently ends in July 2026
                if year == 2026 and month > 7:
                    source_available = False

                # Levels 4–5 only available Jul–Dec 2011
                level_available = (
                    source_available
                    and (
                        level <= 3
                        or (year == 2011 and month >= 7)
                    )
                )

                # Career Compass deliberately starts in Jan 2012
                used = (
                    level_available
                    and year >= 2012
                )

                if used:
                    cell_class = "month-cell used"
                elif level_available:
                    cell_class = "month-cell available"
                else:
                    cell_class = "month-cell empty"

                html += f'<span class="{cell_class}"></span>'

            html += "</div>"

    html += """
    </div>
    <div class="coverage-legend">
        <span><i class="legend-box used"></i>Used in Labour Market Explorer</span>
        <span><i class="legend-box available"></i>Available from BA, not used</span>
    </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_employment_grid():
    start_year = 2011
    end_year = 2026

    html = """
    <div class="coverage-wrap">
        <div class="coverage-grid employment-grid">
    """

    # Top-left cell
    html += '<div class="level-header">KldB</div>'

    # Same year axis as Labour Market grid
    for year in range(start_year, end_year + 1):
        html += f'<div class="year-label">{year}</div>'

    # Five KldB levels
    for level in range(1, 6):
        html += f'<div class="level-label">{level}-digit</div>'

        for year in range(start_year, end_year + 1):
            html += '<div class="quarter-block">'

            for quarter in range(1, 5):

                # Employment source:
                # Dec 2012 through Dec 2025
                source_available = (
                    (year == 2012 and quarter == 4)
                    or (2013 <= year <= 2025)
                )

                if source_available and level in (2, 3):
                    cell_class = "quarter-cell used"

                elif source_available and level == 1:
                    cell_class = "quarter-cell derived"

                elif source_available and level == 4:
                    cell_class = "quarter-cell available"

                else:
                    cell_class = "quarter-cell empty"

                html += f'<span class="{cell_class}"></span>'

            html += "</div>"

    html += """
    </div>
    <div class="coverage-legend">
        <span><i class="legend-box used"></i>Used in Labour Market Explorer</span>
        <span><i class="legend-box derived"></i>Derived in Labour Market Explorer</span>
        <span><i class="legend-box available"></i>Available from BA, not used</span>
    </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)



def render_kldb_hierarchy():

    tree_lines = [
        ('4        Naturwissenschaft, Geografie und Informatik', '10', False),
        ('└─ 43    Informatik-, Informations- und Kommunikationstechnologieberufe', '37', False),
        ('   └─ 431    Informatik', '144', False),
        ('      └─ 4310    Berufe in der Informatik (ohne Spezialisierung)', '702', False),
        ('         └─ 43104    Hoch komplexe Tätigkeiten', '1,300', False),
        ('            ├─ 43104-121    Informatiker/in (Hochschule)', '', False),
        ('            ├─ 43104-132    Data Scientist', '', True),
        ('            └─ 43104-133    Machine Learning Engineer', '', False),
    ]

    tree_html = ""

    for line, count, highlight in tree_lines:
        css_class = (
            "kldb-tree-line tree-highlight"
            if highlight
            else "kldb-tree-line"
        )

        count_html = (
            f'<span class="kldb-tree-count">({count})</span>'
            if count
            else ""
        )

        tree_html += (
            f'<div class="{css_class}">'
            f'<span>{line}</span>'
            f'{count_html}'
            f'</div>'
        )

    html = f"""
<div class="kldb-wrap">

<div class="kldb-layout">

<div class="kldb-tree-section">

<div class="kldb-tree">
{tree_html}
</div>

</div>



</div>

</div>
"""

    html = "\n".join(line.lstrip() for line in html.splitlines())

    st.markdown(
        html,
        unsafe_allow_html=True,
    )




# Mobile About is independent from the legacy desktop data-source layout.
# The two downloadable Parquet files and all original BA/KldB references remain.
import html as _html
from datetime import date as _date
import pandas as _pd
from lme_brand import lme_home_button_style


@st.cache_data(show_spinner=False)
def _about_data_period(path_string: str):
    """Read the *actual* time coverage from the processed file, not a hardcoded date."""
    path = Path(path_string)
    try:
        frame = _pd.read_parquet(path, columns=["report_date"])
        dates = _pd.to_datetime(frame["report_date"], errors="coerce").dropna()
        if len(dates):
            return dates.min().date(), dates.max().date()
    except (OSError, KeyError, ValueError, ImportError):
        pass
    return None, None


def _about_month(day, lang):
    if day is None:
        return "—"
    en = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    de = ("Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez")
    return f"{(de if lang == 'De' else en)[day.month - 1]} {day.year}"


def _about_interval(path, lang):
    low, high = _about_data_period(str(path))
    if low is None:
        return "—", None
    return f"{_about_month(low, lang)} – {_about_month(high, lang)}", high


def _about_last_refresh(lang):
    """Refresh date must be explicitly recorded; Git checkout mtime is not reliable."""
    marker = DATA_DIR / "last_data_update.txt"
    try:
        value = _date.fromisoformat(marker.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return "Noch nicht dokumentiert" if lang == "De" else "Not yet recorded"
    if lang == "De":
        return f"{value.day:02d}.{value.month:02d}.{value.year}"
    return f"{value.day:02d} {_about_month(value, lang)}"


_ABOUT_MOBILE_CSS = """
<style>
@media (max-width: 768px) {
    header[data-testid="stHeader"], [data-testid="stAppHeader"],
    [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important; height: 0 !important; min-height: 0 !important;
    }
    .st-key-lme_about_desktop { display: none !important; }
    .stMainBlockContainer:has(.st-key-lme_about_mobile) {
        padding: .65rem .7rem 2rem !important;
    }
}
@media (min-width: 769px) {
    .st-key-lme_about_mobile { display: none !important; }
}
.st-key-lme_about_mobile {max-width: 470px; margin: 0 auto;}
.st-key-lme_about_mobile_nav [data-testid="stHorizontalBlock"] {
    display: flex !important; flex-flow: row nowrap !important;
    align-items: center !important; justify-content: space-between !important;
}
.st-key-lme_about_mobile_nav [data-testid="stColumn"] {
    flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
}
.st-key-lme_about_mobile_back button {
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: #475467 !important;
    padding: .25rem .35rem !important; white-space: nowrap !important;
}
.lme-about-root {font-family:inherit; color:#26364a;}
.lme-about-root * {box-sizing:border-box;}
.lme-about-hero {
    display:flex; align-items:center; justify-content:space-between;
    background:#344559; color:white; border-radius:15px;
    padding:1rem; margin:.65rem 0 .7rem;
}
.lme-about-hero h1 {color:#fff !important; font-size:1.7rem !important;
    line-height:1.15 !important; font-weight:750 !important; margin:0 0 .3rem !important;
    letter-spacing:0 !important;}
.lme-about-hero p {color:#e0e8f2 !important; font-size:.87rem; line-height:1.42; margin:0;}
.lme-about-hero-mark {display:grid;place-items:center;width:47px;height:47px;
    flex:0 0 47px;border:1px solid #91a9c3;border-radius:12px;
    background:#435d7c;color:#f0f5fb;font-size:1.8rem;font-weight:700;}
.lme-about-card {background:#f8fafd; border:1px solid #e1e6ed;
    border-radius:15px; padding:.9rem; margin:0 0 .65rem;}
.lme-about-card h2 {font-size:1rem !important; font-weight:750 !important;
    margin:0 0 .6rem !important; color:#172438 !important;letter-spacing:0 !important;}
.lme-about-card p {font-size:.86rem; line-height:1.45; margin:.25rem 0; color:#4b5e78;}
.lme-about-period {border-left:3px solid #8ea5c1; padding:.1rem 0 .1rem .65rem; margin:.6rem 0;}
.lme-about-period:last-child {margin-bottom:0;}
.lme-about-period strong {display:block;color:#24364a;font-size:.86rem;}
.lme-about-period small {display:block;color:#53667e; font-size:.78rem; margin-top:.15rem;}
.lme-about-meta {display:flex;justify-content:space-between;gap:.6rem;align-items:baseline;
    font-size:.83rem;margin:.32rem 0;color:#4b5e78;}
.lme-about-meta strong {color:#26384e;text-align:right;}
.lme-about-foot a {color:#345a85 !important; text-decoration:underline;}
.st-key-lme_about_mobile_downloads {background:#f8fafd; border:1px solid #e1e6ed;
    border-radius:15px; padding:.85rem; margin:0 0 .65rem;}
.st-key-lme_about_mobile_downloads [data-testid="stDownloadButton"] button {
    width:100% !important; min-height:46px !important;
    background:#e7edf5 !important; border:1.5px solid #4c627b !important;
    color:#243448 !important; border-radius:10px !important;
    box-shadow:none !important; font-size:.85rem !important; font-weight:700 !important;
}
.st-key-lme_about_mobile_downloads [data-testid="stDownloadButton"] button :is(p,span) {
    color:#243448 !important; -webkit-text-fill-color:#243448 !important;
}
.st-key-lme_about_mobile_downloads [data-testid="stDownloadButton"] button:hover {
    background:#d6e2ef !important; border-color:#344559 !important;
}
.st-key-lme_about_mobile_downloads .lme-about-dl-label {
    font-weight:750;color:#172438;font-size:1rem;margin:0 0 .5rem;
}
.st-key-lme_about_mobile_downloads .lme-about-dl-desc {
    font-size:.77rem;color:#52637a;margin:.35rem 0 .3rem;
}
.st-key-lme_about_mobile_sources [data-testid="stExpander"] {
    background:#f8fafd !important; border-color:#e1e6ed !important;
}
.st-key-lme_about_mobile_sources a {color:#345a85 !important;}
</style>
"""


def _render_mobile_about():
    lang = st.session_state.get("lme_language_preference", st.session_state.get("lme_language", "En"))
    if lang not in ("En", "De"):
        lang = "En"
    de = lang == "De"
    text = lambda en, german: german if de else en
    labour_span, labour_last = _about_interval(labour_parquet, lang)
    employment_span, employment_last = _about_interval(employment_parquet, lang)
    available = max((d for d in (labour_last, employment_last) if d is not None), default=None)
    latest = _about_month(available, lang)
    refresh = _about_last_refresh(lang)
    developer_path = DATA_DIR / "developer_name.txt"
    try:
        developer = developer_path.read_text(encoding="utf-8").strip()
    except OSError:
        developer = ""

    st.html(_ABOUT_MOBILE_CSS)
    with st.container(key="lme_about_mobile"):
        st.markdown(lme_home_button_style(), unsafe_allow_html=True)
        with st.container(key="lme_about_mobile_nav"):
            home_col, back_col = st.columns([1, 1], vertical_alignment="center")
            with home_col:
                if st.button(text("Home", "Startseite"), key="lme_explorer_home",
                             type="tertiary", help=text("Go to Welcome", "Zur Startseite")):
                    st.session_state["lme_screen"] = "welcome"
                    st.switch_page("app.py")
            with back_col:
                if st.button(text("← Back", "← Zurück"), key="lme_about_mobile_back",
                             type="tertiary"):
                    st.session_state["lme_screen"] = "welcome"
                    st.switch_page("app.py")

        # Short, readable information instead of the overflowing year/month matrix.
        intro = text(
            "Official German labour-market statistics from the Federal Employment Agency (BA), organised by KldB occupational groups.",
            "Amtliche deutsche Arbeitsmarktstatistik der Bundesagentur für Arbeit (BA), gegliedert nach Berufsgruppen der KldB.",
        )
        st.html(f"""<div class="lme-about-root">
          <header class="lme-about-hero"><div><h1>{text('About & Data', 'Über & Daten')}</h1>
          <p>{_html.escape(intro)}</p></div><div class="lme-about-hero-mark" aria-hidden="true">i</div></header>
          <section class="lme-about-card"><h2>{text('Data coverage', 'Datenzeiträume')}</h2>
            <div class="lme-about-period"><strong>{text('Vacancies · Unemployed · Job seekers', 'Offene Stellen · Arbeitslose · Arbeitsuchende')}</strong>
              <small>{_html.escape(labour_span)} · {text('monthly', 'monatlich')}</small></div>
            <div class="lme-about-period"><strong>{text('Employed people', 'Beschäftigte')}</strong>
              <small>{_html.escape(employment_span)} · {text('quarterly', 'quartalsweise')}</small></div>
          </section>
          <section class="lme-about-card"><h2>{text('Data currency', 'Datenstand')}</h2>
            <div class="lme-about-meta"><span>{text('Latest period in files', 'Neuester Datenzeitraum')}</span><strong>{_html.escape(latest)}</strong></div>
            <div class="lme-about-meta"><span>{text('Files last refreshed', 'Letzte Dateiaktualisierung')}</span><strong>{_html.escape(refresh)}</strong></div>
          </section>
        </div>""")

        with st.container(key="lme_about_mobile_downloads"):
            st.markdown(f'<div class="lme-about-dl-label">{text("Download data", "Daten herunterladen")}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="lme-about-dl-desc">{text("Vacancies, unemployed people and job seekers · Parquet", "Offene Stellen, Arbeitslose und Arbeitsuchende · Parquet")}</div>',
                        unsafe_allow_html=True)
            if labour_parquet.is_file():
                with labour_parquet.open("rb") as file:
                    st.download_button(text("↓ Download labour-market data", "↓ Arbeitsmarktdaten herunterladen"),
                                       data=file, file_name=labour_parquet.name,
                                       mime="application/octet-stream", key="about_mobile_labour_download", width="stretch")
            else:
                st.error(text("Labour-market file not found", "Arbeitsmarktdatei nicht gefunden"))
            st.markdown(f'<div class="lme-about-dl-desc">{text("Employed people · Parquet", "Beschäftigte · Parquet")}</div>',
                        unsafe_allow_html=True)
            if employment_parquet.is_file():
                with employment_parquet.open("rb") as file:
                    st.download_button(text("↓ Download employment data", "↓ Beschäftigtendaten herunterladen"),
                                       data=file, file_name=employment_parquet.name,
                                       mime="application/octet-stream", key="about_mobile_employment_download", width="stretch")
            else:
                st.error(text("Employment file not found", "Beschäftigtendatei nicht gefunden"))

        with st.container(key="lme_about_mobile_sources"):
            with st.expander(text("Official sources & methodology", "Amtliche Quellen & Methodik")):
                st.markdown("[Arbeitsmarkt nach Berufen (Monatszahlen)](https://statistik.arbeitsagentur.de/SiteGlobals/Forms/Suche/Einzelheftsuche_Formular.html?topic_f=berufe-heft-kldb2010)")
                st.markdown("[Beschäftigte nach Berufen (Quartalszahlen)](https://statistik.arbeitsagentur.de/SiteGlobals/Forms/Suche/Einzelheftsuche_Formular.html?gtp=15084_list%253D51&topic_f=beschaeftigung-sozbe-bo-heft)")
                st.markdown("[KldB 2010 — Band 1 (PDF)](https://statistik.arbeitsagentur.de/DE/Statischer-Content/Grundlagen/Klassifikationen/Klassifikation-der-Berufe/KldB2010-Fassung2020/Printausgabe-KldB-2010-Fassung2020/Generische-Publikationen/KldB2010-PDF-Version-Band1-Fassung2020.pdf?__blob=publicationFile&v=25)")
                st.markdown("[KldB 2010 — Band 2 (PDF)](https://statistik.arbeitsagentur.de/DE/Statischer-Content/Grundlagen/Klassifikationen/Klassifikation-der-Berufe/KldB2010-Fassung2020/Printausgabe-KldB-2010-Fassung2020/Generische-Publikationen/KldB2010-PDF-Version-Band2-Fassung2020.pdf?__blob=publicationFile&v=23)")
        developer_display = _html.escape(developer) if developer else text("Career Compass · WBS final project", "Career Compass · WBS-Abschlussprojekt")
        st.html(f"""<div class="lme-about-root"><section class="lme-about-card lme-about-foot">
            <h2>{text('Developed by', 'Entwickelt von')}</h2>
            <p>{developer_display}</p>
            <p><a href="https://github.com/vkozelchem-spec/career-compass" target="_blank" rel="noopener noreferrer">GitHub · career-compass</a></p>
            </section></div>""")


st.set_page_config(
    page_title="Data Sources | Labour Market Explorer",
    page_icon="🧭",
    layout="wide",
)

apply_app_style()
_render_mobile_about()

with st.container(key="lme_about_desktop"):
    render_header()

    st.markdown(
        """
        <style>
        /* Data Sources page headings */
        h1 {
            font-size: 2rem !important;
        }

        h2 {
            font-size: 1.45rem !important;
            margin-top: 1.6rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
            margin-top: 1.1rem !important;
        }

        .coverage-wrap {
            width: 100%;
            overflow-x: auto;
            margin: 0.6rem 0 1.4rem 0;
            padding-bottom: 0.4rem;
        }

        .coverage-grid {
            display: grid;
            grid-template-columns: 72px repeat(16, minmax(52px, 1fr));
            gap: 5px 7px;
            min-width: 1050px;
            align-items: center;
        }

        .level-header {
            font-size: 0.72rem;
            font-weight: 600;
            color: #667085;
        }

        .year-label {
            text-align: center;
            font-size: 0.72rem;
            font-weight: 600;
            color: #667085;
        }

        .level-label {
            font-size: 0.76rem;
            font-weight: 600;
            color: #344054;
            white-space: nowrap;
        }

        .year-block {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1px;
        }

        .month-cell {
            display: block;
            height: 14px;
            border-radius: 1px;
        }

        .month-cell.used {
            background: #667085;
        }

        .month-cell.available {
            background: #d0d5dd;
        }

        .month-cell.empty {
            background: #f2f4f7;
        }

        .coverage-legend {
            display: flex;
            gap: 1.2rem;
            flex-wrap: wrap;
            margin-top: 0.7rem;
            margin-left: 79px;
            font-size: 0.72rem;
            color: #667085;
        }

        .coverage-legend span {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }

        .legend-box {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }

        .legend-box.used {
            background: #667085;
        }

        .legend-box.available {
            background: #d0d5dd;
        }

    
        .employment-grid {
            grid-template-columns: 72px repeat(16, minmax(52px, 1fr));
        }

        .quarter-block {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2px;
        }

        .quarter-cell {
            display: block;
            height: 14px;
            border-radius: 1px;
        }

        .quarter-cell.used {
            background: #667085;
        }

        .quarter-cell.available {
            background: #d0d5dd;
        }

        .quarter-cell.empty {
            background: #f2f4f7;
        }

        .quarter-cell.derived {
            background: #7f8da3;
        }

        .legend-box.derived {
            background: #7f8da3;
        }

        .dataset-label {
            font-size: 0.88rem;
            font-weight: 600;
            color: #475467;
            margin: 0.35rem 0 0.7rem 0;
        }    

        .kldb-wrap {
            margin: 0.8rem 0 1.5rem 0;
        }

        .kldb-layout {
            display: grid;
            grid-template-columns: minmax(620px, 1.7fr) minmax(340px, 0.8fr);
            gap: 2.2rem;
            align-items: start;
        }

        .kldb-column-title {
            font-size: 0.72rem;
            font-weight: 600;
            color: #667085;
            padding-bottom: 0.55rem;
            margin-bottom: 0.65rem;
            border-bottom: 1px solid rgba(102, 112, 133, 0.25);
        }

        .kldb-tree {
            margin: 0;
            padding: 0;
            background: transparent;
            border: none;

            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.82rem;
            color: #475467;

            overflow-x: auto;
        }

        .kldb-tree-line {
            display: grid;
            grid-template-columns: 620px 70px;
            align-items: center;
            white-space: pre;
            line-height: 2.15;
        }

        .kldb-tree-count {
            text-align: right;
            color: #667085;
            font-size: 0.76rem;
            font-weight: 400;
        }

        .kldb-tree-line.tree-highlight {
            font-weight: 700;
            color: #1d2939;
        }    
    
        .kldb-reference-header,
        .kldb-reference-row {
            display: grid;
            grid-template-columns: 1fr 80px;
            column-gap: 1rem;
        }

        .kldb-reference-header {
            font-size: 0.72rem;
            font-weight: 600;
            color: #667085;

            padding-bottom: 0.55rem;
            border-bottom: 1px solid rgba(102, 112, 133, 0.25);
        }

        .kldb-reference-header span:last-child,
        .kldb-reference-row span:last-child {
            text-align: right;
        }

        .kldb-reference-row {
            min-height: 36px;
            align-items: center;

            font-size: 0.8rem;
            color: #475467;

            border-bottom: 1px solid rgba(102, 112, 133, 0.12);
        }

        .kldb-note {
            margin-top: 0.8rem;
            font-size: 0.72rem;
            color: #667085;
        }        
        

            </style>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------
    # Page title
    # -------------------------------------------------------------------

    st.title("Data Sources")

    st.write(
        "Labour Market Explorer uses official German labour-market data published by the Federal Employment Agency (BA) and structured according to KldB 2010."
    )

    # -------------------------------------------------------------------
    # KldB hierarchy
    # -------------------------------------------------------------------

    st.header("Understanding the KldB Hierarchy")

    st.write(
        "The German Classification of Occupations (KldB 2010) organizes "
        "occupations into five hierarchical levels."
    )

    render_kldb_hierarchy()

    # -------------------------------------------------------------------
    # Data coverage
    # -------------------------------------------------------------------

    st.header("Data Coverage")

    st.markdown(
        '<div class="dataset-label">'
        'Registered Vacancies · Job Seekers · Unemployed People'
        '</div>',
        unsafe_allow_html=True,
    )

    render_labour_market_grid()


    st.markdown(
        '<div class="dataset-label">Employed People</div>',
        unsafe_allow_html=True,
    )

    render_employment_grid()


    # -------------------------------------------------------------------
    # Processed data
    # -------------------------------------------------------------------

    st.header("Download the cleaned datasets used in Labour Market Explorer.")

    col1, col2 = st.columns(2)

    with col1:

        st.caption(
            "Registered Vacancies · Job Seekers · Unemployed People"
        )

        with open(labour_parquet, "rb") as file:
            st.download_button(
                label="Download",
                data=file,
                file_name="german_labour_market_full.parquet",
                mime="application/octet-stream",
                key="download_labour_parquet",
            )


    with col2:

        st.caption("Employed People")

        with open(employment_parquet, "rb") as file:
            st.download_button(
                label="Download",
                data=file,
                file_name="employed_people_full_kldb.parquet",
                mime="application/octet-stream",
                key="download_employment_parquet",
            )


    # -------------------------------------------------------------------
    # Original sources
    # -------------------------------------------------------------------

    st.header("Original Sources")

    source_col1, source_col2 = st.columns(2)

    with source_col1:
        st.markdown("**Labour Market Statistics**")
        st.markdown(
            "[Arbeitsmarkt nach Berufen (Monatszahlen)]"
            "(https://statistik.arbeitsagentur.de/SiteGlobals/Forms/Suche/"
            "Einzelheftsuche_Formular.html?topic_f=berufe-heft-kldb2010)"
        )

    with source_col2:
        st.markdown("**Employment Statistics**")
        st.markdown(
            "[Beschäftigte nach Berufen (Quartalszahlen)]"
            "(https://statistik.arbeitsagentur.de/SiteGlobals/Forms/Suche/"
            "Einzelheftsuche_Formular.html?"
            "gtp=15084_list%253D51&topic_f=beschaeftigung-sozbe-bo-heft)"
        )

    source_col3, source_col4 = st.columns(2)

    with source_col3:
        st.markdown("**KldB 2010, revised 2020 — Volume 1**")
        st.markdown(
            "[Classification structure and methodology]"
            "(https://statistik.arbeitsagentur.de/DE/Statischer-Content/"
            "Grundlagen/Klassifikationen/Klassifikation-der-Berufe/"
            "KldB2010-Fassung2020/Printausgabe-KldB-2010-Fassung2020/"
            "Generische-Publikationen/"
            "KldB2010-PDF-Version-Band1-Fassung2020.pdf?"
            "__blob=publicationFile&v=25)"
        )

    with source_col4:
        st.markdown("**KldB 2010, revised 2020 — Volume 2**")
        st.markdown(
            "[Occupational titles and classifications]"
            "(https://statistik.arbeitsagentur.de/DE/Statischer-Content/"
            "Grundlagen/Klassifikationen/Klassifikation-der-Berufe/"
            "KldB2010-Fassung2020/Printausgabe-KldB-2010-Fassung2020/"
            "Generische-Publikationen/"
            "KldB2010-PDF-Version-Band2-Fassung2020.pdf?"
            "__blob=publicationFile&v=23)"
        )
