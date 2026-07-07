"""
UWC brand styling and shared UI components for the LA_Practice_APP.

Colour palette source: UWC Institutional Planning, Business Intelligence.
"""

import streamlit as st
from pathlib import Path

# ----------------------------------------------------------------------
# Brand colours
# ----------------------------------------------------------------------
UNIVERSITY_BLUE = "#0a1a5c"   # Titles, headers, slicer panel, primary data colour
UNIVERSITY_GOLD = "#bd9a50"   # Highlights, selected emphasis, secondary data colour
MID_BLUE = "#385ba3"          # Alternative series where contrast is needed
LIGHT_GREY = "#d1d1d1"        # Neutral categories, gridlines, support text
MID_GREY = "#3c3c3e"          # Neutral categories, gridlines, support text
CREAM = "#faf6ed"             # Subtle background panels

# Ordered colour sequence for charts (categorical)
CHART_SEQUENCE = [UNIVERSITY_BLUE, UNIVERSITY_GOLD, MID_BLUE, MID_GREY, LIGHT_GREY]

# Risk-level colour mapping used consistently across every page
RISK_COLOURS = {
    "On Track": UNIVERSITY_BLUE,
    "Watch": UNIVERSITY_GOLD,
    "High Risk": MID_GREY,
}

# Flag colour mapping (Yes/No)
FLAG_COLOURS = {"Yes": MID_GREY, "No": UNIVERSITY_BLUE}

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "uwc_logo.png"


def apply_uwc_theme():
    """Inject shared CSS so every page carries consistent UWC branding."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #ffffff;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {UNIVERSITY_BLUE};
        }}
        section[data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
            background-color: {UNIVERSITY_GOLD} !important;
            color: {UNIVERSITY_BLUE} !important;
        }}
        h1, h2, h3 {{
            color: {UNIVERSITY_BLUE};
        }}
        div[data-testid="stMetric"] {{
            background-color: {CREAM};
            border: 1px solid {LIGHT_GREY};
            border-radius: 8px;
            padding: 12px 14px;
        }}
        div[data-testid="stMetric"] label {{
            color: {MID_GREY} !important;
        }}
        .uwc-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 14px;
            font-weight: 600;
            font-size: 0.85rem;
            color: #ffffff;
        }}
        .uwc-callout {{
            background-color: {CREAM};
            border-left: 4px solid {UNIVERSITY_GOLD};
            padding: 14px 18px;
            border-radius: 4px;
            margin-bottom: 12px;
        }}
        .uwc-footer {{
            color: {MID_GREY};
            font-size: 0.8rem;
            border-top: 1px solid {LIGHT_GREY};
            padding-top: 8px;
            margin-top: 24px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = ""):
    """Render the UWC-branded page header with logo."""
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
    with col_title:
        st.markdown(f"<h1 style='margin-bottom:0'>{title}</h1>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(
                f"<p style='color:{MID_GREY};margin-top:4px'>{subtitle}</p>",
                unsafe_allow_html=True,
            )
    st.markdown(
        f"<hr style='border:1px solid {UNIVERSITY_GOLD};margin-top:0'>",
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        "<div class='uwc-footer'>Learning Analytics Progression Dashboard &middot; "
        "LA_Practice_APP &middot; Institutional Planning, Business Intelligence, "
        "University of the Western Cape</div>",
        unsafe_allow_html=True,
    )


def risk_badge(risk_level: str) -> str:
    colour = RISK_COLOURS.get(risk_level, MID_GREY)
    return f"<span class='uwc-badge' style='background-color:{colour}'>{risk_level}</span>"


def flag_badge(flag_value: str) -> str:
    colour = FLAG_COLOURS.get(flag_value, MID_GREY)
    return f"<span class='uwc-badge' style='background-color:{colour}'>{flag_value}</span>"
