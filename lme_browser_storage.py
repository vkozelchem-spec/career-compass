"""A tiny browser-local preference bridge for LME (Streamlit 1.52+).

Only the 'skip welcome' preference is stored in localStorage; no personal data.
"""

import streamlit as st


# This component is registered once per Python module import. It is mounted on
# EVERY main-app rerun, so it is not removed when switching between screens.
_BROWSER_BRIDGE = st.components.v2.component(
    "lme_browser_skip_preference_v1",
    js="""
    export default function({ data, setStateValue }) {
        const storageKey = 'lme_skip_welcome_v2';
        let skip = false;
        try {
            // A Python checkbox callback sets data.write to true/false.
            // null means 'read only' on first connection.
            if (typeof data?.write === 'boolean') {
                window.localStorage.setItem(storageKey, data.write ? '1' : '0');
            }
            skip = window.localStorage.getItem(storageKey) === '1';
        } catch (error) {
            // If storage is blocked, at least preserve the session preference.
            skip = typeof data?.write === 'boolean' ? data.write : false;
        }
        // Updating the same value doesn't cause an extra rerun.
        setStateValue('value', skip);
    }
    """,
)


def browser_skip_welcome(*, write: bool | None = None) -> bool | None:
    """Return saved preference, or None while the browser initializes.

    Passing true/false queues a persistent localStorage write. The caller
    retains that instruction in session_state to withstand rapid navigation.
    """
    result = _BROWSER_BRIDGE(
        key="lme_browser_preference_bridge",
        data={"write": write},
        default={"value": None},
        on_value_change=lambda: None,
    )
    return result.value
