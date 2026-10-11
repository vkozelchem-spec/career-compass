"""Shared, minimalist LME compass mark for Welcome and Explorer."""

import base64


COMPASS_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="12" r="10"/>'
    '<path d="m16.24 7.76-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"/>'
    '</svg>'
)


def lme_compass_button_style() -> str:
    """Make the native, accessible Streamlit navigation button look like the brand."""
    encoded = base64.b64encode(
        COMPASS_SVG.replace('currentColor', '#171717').encode('utf-8')
    ).decode('ascii')
    return f"""<style>
        /* Limited to the Explorer header's home button. */
        .st-key-lme_home_button button {{
            width: auto !important;
            min-height: 2rem !important;
            padding: 0.2rem 0.4rem !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #171717 !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: .45rem !important;
        }}
        .st-key-lme_home_button button::before {{
            content: "";
            display: inline-block;
            width: 20px;
            height: 20px;
            flex: 0 0 20px;
            background-image: url("data:image/svg+xml;base64,{encoded}");
            background-repeat: no-repeat;
            background-size: contain;
            background-position: center;
        }}
        .st-key-lme_home_button button:hover {{
            background: #e9ebef !important;
            color: #171717 !important;
        }}
    </style>"""
