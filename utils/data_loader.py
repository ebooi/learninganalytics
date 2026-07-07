"""
Data loading, caching and shared filter logic for the LA_Practice_APP.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@st.cache_data(show_spinner="Loading programme tracking data...")
def load_programme_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "programme_tracking.csv")
    return df


@st.cache_data(show_spinner="Loading student module level data...")
def load_module_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "student_module_level.csv")
    df["Assessment_Date"] = pd.to_datetime(df["Assessment_Date"])
    return df


MONITORING_ORDER = ["Early", "Mid", "End"]


def sidebar_filters(prog_df: pd.DataFrame, mod_df: pd.DataFrame, include_module: bool = False,
                     include_monitoring: bool = False, key_prefix: str = ""):
    """
    Render a consistent sidebar filter panel and return the filtered
    (programme_df, module_df) tuple plus the selections made.
    """
    st.sidebar.markdown("## Filters")

    years = sorted(prog_df["Academic_Year"].unique())
    sel_years = st.sidebar.multiselect("Academic year", years, default=years, key=f"{key_prefix}_year")

    faculties = sorted(prog_df["Faculty"].unique())
    sel_faculties = st.sidebar.multiselect("Faculty", faculties, default=faculties, key=f"{key_prefix}_fac")

    programmes = sorted(prog_df["Programme_Name"].unique())
    sel_programmes = st.sidebar.multiselect(
        "Programme", programmes, default=programmes, key=f"{key_prefix}_prog"
    )

    year_levels = sorted(prog_df["Year_Level"].unique())
    sel_year_levels = st.sidebar.multiselect(
        "Year of study", year_levels, default=year_levels, key=f"{key_prefix}_yl"
    )

    with st.sidebar.expander("Equity lens filters", expanded=False):
        genders = sorted(prog_df["Gender"].unique())
        sel_genders = st.multiselect("Gender", genders, default=genders, key=f"{key_prefix}_gender")

        nsfas = sorted(prog_df["NSFAS_Flag"].unique())
        sel_nsfas = st.multiselect("NSFAS funded", nsfas, default=nsfas, key=f"{key_prefix}_nsfas")

        residence = sorted(prog_df["Residence_Flag"].unique())
        sel_residence = st.multiselect("Residence", residence, default=residence, key=f"{key_prefix}_res")

        first_gen = sorted(prog_df["First_Generation_Flag"].unique())
        sel_first_gen = st.multiselect(
            "First-generation student", first_gen, default=first_gen, key=f"{key_prefix}_fg"
        )

    prog_filtered = prog_df[
        prog_df["Academic_Year"].isin(sel_years)
        & prog_df["Faculty"].isin(sel_faculties)
        & prog_df["Programme_Name"].isin(sel_programmes)
        & prog_df["Year_Level"].isin(sel_year_levels)
        & prog_df["Gender"].isin(sel_genders)
        & prog_df["NSFAS_Flag"].isin(sel_nsfas)
        & prog_df["Residence_Flag"].isin(sel_residence)
        & prog_df["First_Generation_Flag"].isin(sel_first_gen)
    ].copy()

    student_ids = prog_filtered["STUDENT_NUMBER"].unique()

    mod_filtered = mod_df[mod_df["STUDENT_NUMBER"].isin(student_ids)].copy()

    sel_modules = None
    if include_module:
        modules = sorted(mod_filtered["Module_Name"].unique())
        sel_modules = st.sidebar.multiselect(
            "Module", modules, default=modules, key=f"{key_prefix}_module"
        )
        mod_filtered = mod_filtered[mod_filtered["Module_Name"].isin(sel_modules)]

    sel_monitoring = None
    if include_monitoring:
        sel_monitoring = st.sidebar.multiselect(
            "Monitoring point", MONITORING_ORDER, default=MONITORING_ORDER, key=f"{key_prefix}_mp"
        )
        mod_filtered = mod_filtered[mod_filtered["Monitoring_Point"].isin(sel_monitoring)]

    selections = {
        "years": sel_years,
        "faculties": sel_faculties,
        "programmes": sel_programmes,
        "year_levels": sel_year_levels,
        "genders": sel_genders,
        "nsfas": sel_nsfas,
        "residence": sel_residence,
        "first_gen": sel_first_gen,
        "modules": sel_modules,
        "monitoring": sel_monitoring,
    }

    return prog_filtered, mod_filtered, selections


def latest_monitoring_snapshot(mod_df: pd.DataFrame) -> pd.DataFrame:
    """Return, for each student-module pair, the row for the latest monitoring
    point reached (Early, then Mid, then End), used for 'as at today' flagging."""
    order_map = {m: i for i, m in enumerate(MONITORING_ORDER)}
    df = mod_df.copy()
    df["_mp_order"] = df["Monitoring_Point"].map(order_map)
    df = df.sort_values(["STUDENT_NUMBER", "Module_Code", "Assessment_Date"])
    latest = df.groupby(["STUDENT_NUMBER", "Module_Code"], as_index=False).tail(1)
    return latest.drop(columns="_mp_order")
