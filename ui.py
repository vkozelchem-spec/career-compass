from pathlib import Path

import streamlit as st


ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "LME.png"


def apply_app_style() -> None:
    """Apply the shared visual style used across the application."""

    st.markdown(
        """
        <style>

        /* Page background */
        .stApp {
            background:
                radial-gradient(
                    circle at 10% 10%,
                    rgba(90, 140, 220, 0.18),
                    transparent 35%
                ),
                radial-gradient(
                    circle at 90% 15%,
                    rgba(170, 120, 220, 0.14),
                    transparent 40%
                ),
                radial-gradient(
                    circle at 50% 90%,
                    rgba(80, 180, 190, 0.10),
                    transparent 40%
                ),
                linear-gradient(
                    135deg,
                    #f7f9fc 0%,
                    #eef3f9 50%,
                    #f8f9fc 100%
                );

            background-attachment: fixed;
        }

        /* Hide Streamlit's default multipage sidebar navigation */
        [data-testid="stSidebar"] {
            display: none;
        }

        /* Hide the sidebar expand/collapse control */
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }

        /* Header navigation buttons */
        div[data-testid="stButton"] > button {
            background: transparent;
            border: none;
            box-shadow: none;
            padding: 0.35rem 0.6rem;
            font-weight: 500;
            color: #334155;
        }

        div[data-testid="stButton"] > button:hover {
            background: rgba(255, 255, 255, 0.35);
            border: none;
            color: #0f172a;
        }

        div[data-testid="stButton"] > button:focus {
            box-shadow: none;
        }

        /* Selectbox / multiselect focus border */
        div[data-baseweb="select"] > div:focus-within {
            border-color: #64748B !important;
            box-shadow: 0 0 0 1px #64748B !important;
        }

        /* Selectbox background */
        [data-testid="stSelectbox"] div[role="group"] {
            background: rgba(255, 255, 255, 0.85) !important;
        }

        /* Selectbox focus border */
        [data-testid="stSelectbox"] [role="group"][data-focus-within] {
            border-color: #64748B !important;
        }
        
        /* Selected multiselect tags */
        span[data-tag] {
            background: #64748B !important;
            color: white !important;
        }

        /* Selected segmented-control options */
        button[data-variant="segmented_control"][data-selected="true"] {
            background: #64748B !important;
            color: white !important;
            border-color: #64748B !important;
        }

        /* Glass-style chart settings */
        [data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.65);
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(31, 38, 135, 0.08);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            overflow: hidden;
        }

        /* Glass-style chart cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.42);
            border: 1px solid rgba(255, 255, 255, 0.70) !important;
            border-radius: 18px;
            box-shadow: 0 8px 30px rgba(31, 38, 135, 0.08);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
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
            nav_spacer, nav_layout, nav_dashboard, nav_sources, nav_about = st.columns(
                [3.5, 1.2, 1.2, 1.3, 1],
                vertical_alignment="center",
            )
        else:
            nav_spacer, nav_dashboard, nav_sources, nav_about = st.columns(
                [5, 1.2, 1.3, 1],
                vertical_alignment="center",
            )

    if show_layout_control:
        with nav_layout:
            layout_label = (
                "Grid view"
                if st.session_state.get("chart_layout", "Vertical") == "Vertical"
                else "Vertical view"
            )

            if st.button(
                layout_label,
                key="nav_layout",
                use_container_width=True,
            ):
                st.session_state.chart_layout = (
                    "Grid"
                    if st.session_state.get("chart_layout", "Vertical") == "Vertical"
                    else "Vertical"
                )
                st.rerun()

        layout_mode = st.session_state.get(
            "chart_layout",
            "Vertical",
        )
    else:
        layout_mode = None

    with nav_dashboard:
        if st.button(
            "Dashboard",
            key="nav_dashboard",
            use_container_width=True,
        ):
            st.switch_page("app.py")

    with nav_sources:
        if st.button(
            "Data Sources",
            key="nav_data_sources",
            use_container_width=True,
        ):
            st.switch_page("pages/data_sources.py")

    with nav_about:
        st.button(
            "About",
            key="nav_about",
            use_container_width=True,
        )

    return layout_mode