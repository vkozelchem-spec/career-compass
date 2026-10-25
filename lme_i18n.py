"""Explorer EN/DE user-facing strings; language never changes data keys."""

DE = {
    "Occupation:": "Beruf:",
    "Occupation · Categories": "Beruf · Kategorien",
    "Occupation · Subcategories": "Beruf · Unterkategorien",
    "‹ Back": "‹ Zurück",
    "Previous category, or return to Search": "Übergeordnete Kategorie oder Suche öffnen",
    "Go to the parent occupation category": "Zur übergeordneten Berufsgruppe",
    "Search occupations": "Berufe suchen",
    "Search occupations alphabetically": "Berufe alphabetisch suchen",
    "Categories": "Kategorien",
    "No further categories": "Keine Unterkategorien",
    "Choose a subcategory": "Unterkategorie auswählen",
    "No further subcategories": "Keine weiteren Unterkategorien",
    "No further subcategories; use Back to go up a level": "Keine Unterkategorien; mit Zurück eine Ebene höher",
    "Return to alphabetical search": "Zur alphabetischen Suche",
    "Browse occupations by category": "Berufe nach Kategorien durchsuchen",
    "Qualification:": "Qualifikation:",
    "Qualification level": "Anforderungsniveau",
    "No qualification data is available for this occupation.": "Für diesen Beruf sind keine Qualifikationsdaten verfügbar.",
    "No qualification data": "Keine Qualifikationsdaten",
    "Choose at least one indicator in the legend below.": "Bitte mindestens eine Kennzahl in der Legende auswählen.",
    "No time series is available for this selection.": "Für diese Auswahl ist keine Zeitreihe verfügbar.",
    "Selection": "Auswahl",
    "Hide": "Ausblenden",
    "Show": "Einblenden",
    "for both occupations": "für beide Berufsgruppen",
    "Vacancies": "Offene Stellen",
    "Employed": "Beschäftigte",
    "Unemployed": "Arbeitslose",
    "Job seekers": "Arbeitsuchende",
    "Registered vacancies": "Gemeldete offene Stellen",
    "Employed people": "Beschäftigte",
    "Unemployed people": "Arbeitslose",
    "Date": "Datum",
    "Indicator": "Kennzahl",
    "Value": "Wert",
    "Index": "Index",
    "Index (start = 100)": "Index (Start = 100)",
    "All occupations": "Alle Berufe",
    "Overall": "Insgesamt",
    "Helpers": "Helfer",
    "Skilled": "Fachkräfte",
    "Specialists": "Spezialisten",
    "Experts": "Experten",
    "Home": "Startseite",
    "Back to Welcome": "Zur Startseite",
    "Absolute values": "Absolute Werte",
    "Indexed (start = 100)": "Indexiert (Start = 100)",
    "Indexed (start = 100), not percentages": "Indexiert (Start = 100), keine Prozentwerte",
    "Exit comparison": "Vergleich beenden",
    "Compare occupations": "Berufe vergleichen",
    "Return to one chart": "Zur Einzelansicht",
    "Compare two occupations (Overlay)": "Zwei Berufe überlagert vergleichen",
    "Chart layout": "Diagrammansicht",
    "Occupation label language": "Sprache",
    "One": "Einzeln",
    "Two": "Zwei",
    "Overlay": "Überlagert",
    "Dashboard": "Diagramme",
    "About": "Über",
    "Open Welcome": "Startseite öffnen",
}

INDICATORS = {
    "Vacancies": "Offene Stellen", "Employed": "Beschäftigte",
    "Unemployed": "Arbeitslose", "Job seekers": "Arbeitsuchende",
    "Registered vacancies": "Gemeldete offene Stellen",
    "Employed people": "Beschäftigte", "Unemployed people": "Arbeitslose",
}

QUALIFICATION_DISPLAY = {
    "En": {"Insgesamt": "Overall", "Gesamt": "Overall", "Helfer": "Helpers",
           "Fachkraft": "Skilled", "Spezialist": "Specialists", "Experte": "Experts"},
    "De": {"Insgesamt": "Insgesamt", "Gesamt": "Insgesamt", "Helfer": "Helfer",
           "Fachkraft": "Fachkräfte", "Spezialist": "Spezialisten", "Experte": "Experten"},
}
QUALIFICATION_TABS = {
    "En": {"Insgesamt": "All", "Gesamt": "All", "Helfer": "Helper",
           "Fachkraft": "Skilled", "Spezialist": "Specialist", "Experte": "Expert"},
    "De": {"Insgesamt": "Alle", "Gesamt": "Alle", "Helfer": "Helfer",
           "Fachkraft": "Fachkraft", "Spezialist": "Spezialist", "Experte": "Experte"},
}
QUALIFICATION_MOBILE_TABS = {
    "En": QUALIFICATION_TABS["En"],
    "De": {"Insgesamt": "Alle", "Gesamt": "Alle", "Helfer": "Helfer",
           "Fachkraft": "Fachkr.", "Spezialist": "Spez.", "Experte": "Experte"},
}

QUALIFICATION_SHORT = {
    "En": {"Insgesamt": "All", "Gesamt": "All", "Helfer": "Helper",
           "Fachkraft": "Skilled", "Spezialist": "Specialist", "Experte": "Expert"},
    "De": {"Insgesamt": "Alle", "Gesamt": "Alle", "Helfer": "Helfer",
           "Fachkraft": "Fachkraft", "Spezialist": "Spez.", "Experte": "Experte"},
}


def tr(text: str, lang: str) -> str:
    return DE.get(text, text) if lang == "De" else text
