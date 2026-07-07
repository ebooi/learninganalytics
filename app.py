import streamlit as st

from utils.styling import apply_uwc_theme, render_header, render_footer, UNIVERSITY_BLUE, UNIVERSITY_GOLD
from utils.data_loader import load_programme_data, load_module_data

st.set_page_config(
    page_title="LA_Practice_APP | Learning Analytics Progression Dashboard",
    page_icon="🎓",
    layout="wide",
)

apply_uwc_theme()
render_header(
    "Learning Analytics Progression Dashboard",
    "LA_Practice_APP &middot; Institutional Planning, Business Intelligence &middot; University of the Western Cape",
)

prog_df = load_programme_data()
mod_df = load_module_data()

st.markdown(
    """
This app turns assessment and progression data into decision-ready views for four
audiences in the faculty: the Dean and Deputy Deans, the Faculty Manager, module
lecturers, and students themselves. Its purpose is to surface, as early as possible
and again at the end of the assessment cycle, which students are not submitting
assessments, which are failing, and how each student compares with the class and
programme average, so that the right person can act in time.
"""
)

st.markdown("### At a glance")

col1, col2, col3, col4, col5 = st.columns(5)
total_students = prog_df["STUDENT_NUMBER"].nunique()
high_risk_pct = (prog_df["Progression_Risk_Level"] == "High Risk").mean() * 100
watch_pct = (prog_df["Progression_Risk_Level"] == "Watch").mean() * 100
non_sub_rate = (mod_df["Non_Submission_Flag"] == "Yes").mean() * 100
fail_rate = (mod_df["Failed_Assessment_Flag"] == "Yes").mean() * 100

col1.metric("Students tracked", f"{total_students:,}")
col2.metric("Programmes", f"{prog_df['Programme_Code'].nunique()}")
col3.metric("High risk", f"{high_risk_pct:.1f}%")
col4.metric("On watch", f"{watch_pct:.1f}%")
col5.metric("Assessment non-submission rate", f"{non_sub_rate:.1f}%")

st.markdown("---")
st.markdown("### Navigate by role")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.markdown(
        f"""
        <div class="uwc-callout">
        <b style="color:{UNIVERSITY_BLUE}">Dean and Deputy Deans' View</b><br>
        Faculty-wide strategic picture: risk distribution across programmes,
        equity patterns, and the effect of early intervention. Use this to
        decide where faculty-level attention and resourcing are needed.
        </div>
        <div class="uwc-callout">
        <b style="color:{UNIVERSITY_BLUE}">Faculty Manager View</b><br>
        Operational detail across modules and monitoring points: non-submission
        and failure hotspots, gateway module performance, and downloadable
        at-risk lists for coordination with lecturers and student support.
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col2:
    st.markdown(
        f"""
        <div class="uwc-callout">
        <b style="color:{UNIVERSITY_BLUE}">Lecturer View</b><br>
        Module-level tracking: class progress across assessments, students
        who are not submitting or are failing, and who to contact first.
        </div>
        <div class="uwc-callout">
        <b style="color:{UNIVERSITY_BLUE}">Student View</b><br>
        A personal dashboard comparing a student's own average with the class
        and programme average, credit completion progress, and a clear next
        step.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("### Supporting pages")
st.markdown(
    """
- **Data Quality** — completeness, consistency and validity checks on the underlying data, refreshed each time the app runs.
- **Data Definitions** — the data dictionary and the methodology behind every flag, average and risk tier used across the dashboard.
"""
)

st.info(
    "Use the sidebar navigation on the left to move between views. Every view "
    "carries the same filter logic (academic year, faculty, programme, year of "
    "study and equity lens), so a Dean and a lecturer can compare the same "
    "students from different angles.",
    icon="ℹ️",
)

render_footer()
