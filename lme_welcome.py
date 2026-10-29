"""Responsive LME welcome screen (single-photo, compact version).

Independent from the data-loading/chart logic. The caller owns navigation.
Browser persistence is handled by the app-level preference callback.
"""

from typing import Callable
import base64
import html
import io
from pathlib import Path
from urllib.request import Request, urlopen

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
    row-gap: .85rem;
    align-items: center;
    max-width: 1450px;
    margin: clamp(1.6rem, 4vh, 3rem) auto 1.3rem;
}
.lme-welcome-heading { grid-area: heading; align-self: end; }
.lme-welcome-graph { grid-area: graph; min-width: 0; }
.lme-welcome-benefits { grid-area: benefits; align-self: start; }
.lme-welcome-headline {
    margin: 0;
    font-size: clamp(2.08rem, 3vw, 3.08rem);
    line-height: 1.12;
    font-weight: 800;
    letter-spacing: -.003em;
    color: #171717;
}
.lme-welcome-headline .lme-welcome-line { white-space: nowrap; }
/* Static documentary photo. Locally embedded, so it never hotlinks in browsers. */
.lme-welcome-preview { width: 100%; min-width: 0; }
.lme-welcome-photo {
    width: 100%;
    aspect-ratio: 2.30 / 1;
    overflow: hidden;
    background: #cbd2da;
    border-radius: 15px;
    box-shadow: 0 4px 18px rgba(16, 24, 40, .09);
}
.lme-welcome-photo img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 45%;
}
.lme-welcome-photo-unavailable {
    aspect-ratio: 2.30 / 1;
    display: grid;
    place-items: center;
    border: 1px solid #cbd2da;
    border-radius: 15px;
    color: #394758;
    font-size: .88rem;
    text-align: center;
    padding: 1rem;
}
.lme-welcome-description {
    margin: 0;
    max-width: 34rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #394758;
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
/* Agreed outlined secondary CTA. */
.st-key-lme_welcome_help_link button {
    width: 100% !important;
    min-height: 3.15rem !important;
    padding: .5rem 1rem !important;
    background: transparent !important;
    border: 1.5px solid #394758 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    color: #394758 !important;
    font-weight: 700 !important;
}
.st-key-lme_welcome_help_link button:hover {
    background: rgba(57,71,88,.06) !important;
    color: #27394a !important;
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
    .st-key-lme_welcome_actions[data-testid="stVerticalBlock"]:has(.st-key-lme_welcome_explore):has(.st-key-lme_welcome_skip_area):not(:has(.st-key-lme_welcome_help_link)),
    .st-key-lme_welcome_actions [data-testid="stVerticalBlock"]:has(.st-key-lme_welcome_explore):has(.st-key-lme_welcome_skip_area):not(:has(.st-key-lme_welcome_help_link)) {
        display: flex !important;
        flex-direction: column-reverse !important;
    }
    .st-key-lme_welcome_skip_area {
        padding-top: 0;
        padding-bottom: .35rem;
    }
}
@media (min-width: 1024px) {
    .lme-welcome-description {
        font-size: clamp(1.035rem, 1.1vw, 1.18rem);
    }
}
@media (max-width: 768px) {
    .lme-welcome-grid {
        grid-template-columns: minmax(0, 1fr);
        grid-template-areas: "heading" "graph" "benefits";
        /* Bring the headline close to the minimal About link. */
        row-gap: .3rem;
        margin-top: -1.95rem;
        margin-bottom: .1rem;
    }
    .lme-welcome-heading, .lme-welcome-benefits { align-self: auto; }
    /* Fine-tune only the mobile composition. Desktop stays untouched. */
    /* Less blank space between the title and the image. */
    .lme-welcome-graph { margin-top: -.82rem; }
    .lme-welcome-headline {
        font-size: clamp(2rem, 10vw, 2.5rem);
        line-height: 1.1;
    }
    /* On phones, show the COMPLETE documentary photograph instead of
       cropping it to a shallow banner. The surrounding workplace remains
       visible, while desktop keeps its original panoramic composition. */
    .lme-welcome-photo {
        aspect-ratio: auto;
        height: auto;
    }
    .lme-welcome-photo img {
        width: 100%;
        height: auto;
        object-fit: contain;
        object-position: center;
    }
    .lme-welcome-photo-unavailable { aspect-ratio: 2.10 / 1; }
    .lme-welcome-description { font-size: .95rem; line-height: 1.45; }
    .st-key-lme_welcome_explore { max-width: none; }
    /* Keep the lower-right Streamlit hosting badge away from the checkbox. */
    .st-key-lme_welcome_skip_area {
        padding-right: 5.5rem;
        padding-bottom: max(4.5rem, env(safe-area-inset-bottom));
    }
}
</style>
"""


# The bucket photo is for local prototype testing only. Redistribution rights
# have not been confirmed; clear permission or replace it before publishing.
_BUCKET_PHOTO = (
    "workers_bucket",
    "https://www.loopbaancentraal.nl/resources/uploads/images/schaftpauze_medewerkers_bouw.jpg",
)


def _photo_uri(stem: str, url: str) -> str | None:
    """Serve the original photo as a local inline image; download once if needed.

    Users may also place `assets/welcome/<stem>.jpg` or `.png` manually.
    No external browser hotlinking is needed once the image is available.
    """
    folder = Path(__file__).resolve().parent / "assets" / "welcome"
    existing = next((folder / f"{stem}{ext}" for ext in (".jpg", ".jpeg", ".png")
                    if (folder / f"{stem}{ext}").is_file()), None)
    if existing is None:
        if st.session_state.get(f"lme_photo_download_failed_{stem}"):
            return None
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; LME-Welcome-prototype/1.0)",
                "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*",
            })
            with urlopen(req, timeout=7) as response:
                raw = response.read(9_000_000)
            is_jpeg = raw.startswith(b"\xff\xd8\xff")
            is_png = raw.startswith(b"\x89PNG\r\n\x1a\n")
            if len(raw) < 5000 or not (is_jpeg or is_png):
                raise ValueError("Response was not a supported image")
            folder.mkdir(parents=True, exist_ok=True)
            existing = folder / f"{stem}{'.jpg' if is_jpeg else '.png'}"
            existing.write_bytes(raw)
        except (OSError, ValueError, TimeoutError) as exc:
            # Only a local preview: do not stop Welcome/Explorer from loading.
            st.session_state[f"lme_photo_download_failed_{stem}"] = str(exc)
            return None

    try:
        raw = existing.read_bytes()
        if raw.startswith(b"\xff\xd8\xff"):
            media = "image/jpeg"
        elif raw.startswith(b"\x89PNG\r\n\x1a\n"):
            media = "image/png"
        else:
            return None
        # Optional optimization: reduce the large Wikimedia original from
        # ~5 MB to a web-sized JPEG when Pillow is installed in the project.
        try:
            from PIL import Image
            image = Image.open(io.BytesIO(raw))
            if image.width > 1600 or len(raw) > 1_000_000:
                image.thumbnail((1600, 1100))
                out = io.BytesIO()
                image.convert("RGB").save(out, format="JPEG", quality=83, optimize=True)
                raw = out.getvalue()
                media = "image/jpeg"
        except (ImportError, OSError):
            pass
        return f"data:{media};base64,{base64.b64encode(raw).decode('ascii')}"
    except OSError:
        return None


def _welcome_photo_html(lang: str) -> tuple[str, bool]:
    """Return one static photograph HTML fragment and its availability status."""
    uri = _photo_uri(*_BUCKET_PHOTO)
    if not uri:
        msg = (
            "Photo unavailable — see installation instructions"
            if lang == "En" else
            "Foto nicht verfügbar – siehe Installationsanleitung"
        )
        return f'<div class="lme-welcome-photo-unavailable">{html.escape(msg)}</div>', True
    alt = (
        "Construction workers eating lunch in a front-loader bucket"
        if lang == "En" else
        "Bauarbeiter bei der Mittagspause in einer Radladerschaufel"
    )
    return (f'<div class="lme-welcome-photo">'
            f'<img src="{uri}" alt="{html.escape(alt, quote=True)}">'
            '</div>'), False


_WELCOME_CONTENT = """
<div class="lme-welcome-grid">
  <div class="lme-welcome-heading">
    <h1 class="lme-welcome-headline">{headline}</h1>
  </div>
  <div class="lme-welcome-graph">
    <div class="lme-welcome-preview">{photo}</div>
  </div>
  <div class="lme-welcome-benefits">
    <p class="lme-welcome-description">{description}</p>
  </div>
</div>
"""


def render_welcome(
    on_explore: Callable[[], None],
    on_about: Callable[[], None],
    skip_default: bool = False,
    on_skip_change: Callable[[], None] | None = None,
    language: str = "En",
    on_help: Callable[[], None] | None = None,
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

    photo, missing_photo = _welcome_photo_html(lang)
    # Localized copy is kept here so this visual-only patch requires no
    # changes to shared Explorer and Help translations.
    headline = (
        '<span class="lme-welcome-line">Labour market</span><br>'
        '<span class="lme-welcome-line">in numbers.</span>'
        if lang == "En" else
        '<span class="lme-welcome-line">Arbeitsmarkt</span><br>'
        '<span class="lme-welcome-line">in Zahlen.</span>'
    )
    description = (
        "Compare occupations. Follow employment, unemployment and vacancies over time."
        if lang == "En" else
        "Berufe vergleichen. Beschäftigung, Arbeitslosigkeit und offene Stellen im Zeitverlauf verfolgen."
    )
    content = _WELCOME_CONTENT.format(
        headline=headline,
        photo=photo,
        description=html.escape(description),
    )
    st.markdown(content, unsafe_allow_html=True)
    if missing_photo:
        st.caption(
            "Welcome photo unavailable. See README for local image installation."
            if lang == "En" else
            "Welcome-Foto fehlt. Siehe README zur lokalen Installation."
        )

    with st.container(key="lme_welcome_actions"):
        if st.button(f"{tr('Start exploring', lang)} →", key="lme_welcome_explore", width="stretch"):
            on_explore()
        if on_help is not None:
            with st.container(key="lme_welcome_help_link"):
                if st.button(f"{tr('How it works', lang)} →", key="lme_welcome_help", type="tertiary", width="stretch"):
                    on_help()
        with st.container(key="lme_welcome_skip_area"):
            skip = st.checkbox(
                tr("Don't show this again", lang),
                key="lme_skip_welcome",
                on_change=on_skip_change,
            )

    return skip
