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


# Explorer navigation has a different role than the compass brand mark.
# The Welcome page can keep COMPASS_SVG; the Explorer uses a Home icon.
HOME_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
    'viewBox="0 0 24 24" fill="none" stroke="#171717" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true" focusable="false">'
    '<path d="m3 10 9-7 9 7"/>'
    '<path d="M5 10v10h14V10"/>'
    '<path d="M9 20v-6h6v6"/>'
    '</svg>'
)


def lme_home_button_style() -> str:
    """A clean SVG house with an off-screen, screen-reader-readable Home label."""
    encoded = base64.b64encode(HOME_SVG.encode("utf-8")).decode("ascii")
    return f"""<style>
        .st-key-lme_explorer_home button {{
            width: 42px !important;
            min-width: 42px !important;
            height: 40px !important;
            min-height: 40px !important;
            padding: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 1px solid transparent !important;
            border-radius: 9px !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #171717 !important;
            position: relative !important;
        }}
        /* Keep "Home" as the accessible label, but hide it visually. */
        .st-key-lme_explorer_home button p {{
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            overflow: hidden !important;
            clip-path: inset(50%) !important;
            white-space: nowrap !important;
        }}
        .st-key-lme_explorer_home button::before {{
            content: "";
            display: block;
            width: 21px;
            height: 21px;
            flex: 0 0 21px;
            background-image: url("data:image/svg+xml;base64,{encoded}");
            background-repeat: no-repeat;
            background-size: contain;
            background-position: center;
        }}
        .st-key-lme_explorer_home button:hover {{
            background: #e9ebef !important;
        }}
        .st-key-lme_explorer_home button:focus-visible {{
            outline: 2px solid #667085 !important;
            outline-offset: 2px !important;
        }}
    </style>"""
