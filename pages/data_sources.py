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



st.set_page_config(
    page_title="Data Sources | Labour Market Explorer",
    page_icon="🧭",
    layout="wide",
)

apply_app_style()
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
