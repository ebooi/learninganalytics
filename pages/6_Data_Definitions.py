import pandas as pd
import streamlit as st

from utils.styling import apply_uwc_theme, render_footer, render_header

st.set_page_config(page_title="Data Definitions | LA_Practice_APP", page_icon="📖", layout="wide")
apply_uwc_theme()
render_header(
    "Data Definitions",
    "The data dictionary and methodology behind every metric, flag and risk tier used in this dashboard.",
)

st.markdown(
    "This page is the reference companion to every other view in LA_Practice_APP. If a term, average or "
    "flag is unclear anywhere in the dashboard, its definition is here."
)

# ---------------------------------------------------------------------
# Programme Tracking data dictionary
# ---------------------------------------------------------------------
st.markdown("### Programme Tracking sheet")

programme_dict = [
    ("STUDENT_NUMBER", "Unique student identifier."),
    ("Academic_Year", "The academic year the record relates to."),
    ("Faculty", "Faculty to which the student's programme belongs."),
    ("Programme_Code", "Short code for the qualification, e.g. BCOM."),
    ("Programme_Name", "Full name of the qualification."),
    ("Programme_Duration_Years", "Standard duration of the qualification in years."),
    ("Year_Level", "The student's current year of study within the qualification."),
    ("Gender", "Self-identified gender, used for equity monitoring."),
    ("Race", "Population group, used for equity monitoring in line with sector reporting norms."),
    ("NSFAS_Flag", "Whether the student receives NSFAS funding."),
    ("Residence_Flag", "Whether the student lives in university residence."),
    ("First_Generation_Flag", "Whether the student is the first in their family to attend university."),
    ("Entry_APS_Band", "Admission Point Score band at entry, grouped into ranges."),
    ("Expected_Credits_ToDate", "Credits the student should have accumulated by this point, given a normal pace."),
    ("Prior_Credits_Passed", "Credits passed in years prior to the current academic year."),
    ("Current_Year_Expected_Credits", "Credits expected to be completed within the current academic year."),
    ("Current_Credits_Passed", "Credits passed so far within the current academic year."),
    ("Total_Credits_Passed", "Prior credits passed plus current credits passed."),
    ("Credit_Completion_Current_Pct", "Current_Credits_Passed divided by Current_Year_Expected_Credits."),
    ("Credit_Completion_ToDate_Pct", "Total_Credits_Passed divided by Expected_Credits_ToDate."),
    ("Current_Module_Count", "Number of modules the student is registered for this year."),
    ("Failed_Module_Count", "Number of modules not yet passed this year."),
    ("Failed_Gateway_Module_Count", "Number of gateway modules not yet passed this year."),
    ("Non_Submitted_Assessment_Count", "Total assessments not submitted across all modules this year."),
    ("Failed_Assessment_Count", "Total submitted assessments scoring below the pass mark this year."),
    ("Student_Overall_CA_Average", "The student's average continuous assessment mark to date, across modules."),
    ("Student_Final_Average", "The student's overall average mark for the year, across modules."),
    ("Programme_Final_Average", "The average final mark of all students in the same programme and year level."),
    ("Difference_From_Programme_Avg", "Student_Final_Average minus Programme_Final_Average."),
    ("Early_At_Risk_Flag", "Whether the student was flagged at risk at the early monitoring point."),
    ("End_At_Risk_Flag", "Whether the student was flagged at risk at the end monitoring point."),
    ("Progression_Risk_Level", "Overall risk tier: On Track, Watch, or High Risk. See methodology below."),
    ("Recommended_Action", "The suggested intervention associated with the student's risk tier."),
    ("Equity_Review_Group", "Combined gender, NSFAS and residence grouping used for equity-lens analysis."),
]

st.dataframe(
    pd.DataFrame(programme_dict, columns=["Field", "Definition"]),
    use_container_width=True,
    height=520,
    hide_index=True,
)

st.markdown("---")

# ---------------------------------------------------------------------
# Student Module Level data dictionary
# ---------------------------------------------------------------------
st.markdown("### Student Module Level sheet")

module_dict = [
    ("STUDENT_NUMBER", "Unique student identifier, links to the Programme Tracking sheet."),
    ("Academic_Year", "The academic year the record relates to."),
    ("Faculty", "Faculty to which the student's programme belongs."),
    ("Programme_Code / Programme_Name", "The student's programme, repeated at module level for filtering."),
    ("Year_Level", "The student's year of study."),
    ("Gender / Race / NSFAS_Flag / Residence_Flag", "Equity attributes, repeated at module level for filtering."),
    ("Module_Code / Module_Name", "The module the assessment belongs to."),
    ("Gateway_Module_Flag", "Whether the module is a gateway module, i.e. a strong predictor of overall progression."),
    ("Module_Credits", "Credit value of the module."),
    ("Assessment_ID / Assessment_Name", "Identifier and name of the specific assessment."),
    ("Assessment_Type", "Quiz, Assignment, Test, or Exam."),
    ("Assessment_Date", "The date the assessment was due or written."),
    ("Monitoring_Point", "Early, Mid, or End, indicating where this assessment sits in the assessment cycle."),
    ("Assessment_Weight", "The percentage weight of this assessment toward the module's continuous assessment mark."),
    ("Assessment_Status", "Submitted, Late, or Not Submitted."),
    ("Submitted_Flag", "Yes or No, derived from Assessment_Status."),
    ("Assessment_Mark", "The raw mark achieved, out of 100, or 0 where not submitted."),
    ("Mark_For_Progress", "The mark used for progress tracking; equivalent to Assessment_Mark in this dataset."),
    ("Weighted_Mark_Contribution", "Assessment_Mark multiplied by Assessment_Weight, divided by 100."),
    ("Cumulative_Assessment_Weight_ToDate", "Running total of assessment weight covered so far in the module."),
    ("Cumulative_Progress_Percentage", "Running total of weighted mark contribution as a percentage of weight covered."),
    ("Cumulative_CA_Average_ToDate", "The student's continuous assessment average in the module to date."),
    ("Class_Average_Assessment", "The average mark for this specific assessment across the whole class."),
    ("Difference_From_Class_Avg", "The student's mark minus the class average for this assessment."),
    ("Programme_Average_Assessment", "The average mark for this specific assessment across the whole programme."),
    ("Difference_From_Programme_Avg", "The student's mark minus the programme average for this assessment."),
    ("Non_Submission_Flag", "Yes where Assessment_Status is Not Submitted."),
    ("Failed_Assessment_Flag", "Yes where the assessment was submitted and scored below the pass mark of 50."),
    ("Below_Class_Avg_Flag", "Yes where the student's mark is below the class average for this assessment."),
    ("Below_Programme_Avg_Flag", "Yes where the student's mark is below the programme average for this assessment."),
    ("Early_Alert_Flag", "Yes where this assessment record triggers at least one alert condition."),
    ("Alert_Reason", "The specific condition(s) that triggered the Early_Alert_Flag, semicolon-separated."),
]

st.dataframe(
    pd.DataFrame(module_dict, columns=["Field", "Definition"]),
    use_container_width=True,
    height=560,
    hide_index=True,
)

st.markdown("---")

# ---------------------------------------------------------------------
# Methodology
# ---------------------------------------------------------------------
st.markdown("### Methodology notes")

st.markdown("#### Monitoring points")
st.markdown(
    "Every assessment is tagged to one of three monitoring points across the year: **Early**, **Mid**, and "
    "**End**. This allows the same at-risk logic to be applied as early as possible in the cycle, when "
    "intervention is most useful, and again at the end, when the outcome is confirmed."
)

st.markdown("#### Risk tiers")
st.markdown(
    """
- **On Track**: no active flags; the student is progressing in line with expectations.
- **Watch**: the student has at least one flag (a non-submission, a failed assessment, or a mark below
  average) but is not yet in serious difficulty.
- **High Risk**: multiple flags are present, often including a failed gateway module or a large negative
  gap to the programme average, indicating the student needs urgent, coordinated support.
"""
)

st.markdown("#### Early vs end at-risk comparison")
st.markdown(
    "**Early_At_Risk_Flag** and **End_At_Risk_Flag** are calculated independently at their respective "
    "monitoring points, using the same rules. Comparing the two identifies four groups, used throughout the "
    "Dean and Deputy Deans' View: students never at risk, students who were at risk early and resolved this "
    "by the end (a sign that early intervention worked), students whose risk persisted, and students whose "
    "risk only emerged later (a sign that earlier monitoring may need to be more sensitive)."
)

st.markdown("#### Class and programme averages")
st.markdown(
    "Every assessment mark is compared against two benchmarks calculated at the same monitoring point: the "
    "**class average** (all students in the same module) and the **programme average** (all students in the "
    "same programme and year level). This is what allows a lecturer to see whether a student is behind their "
    "immediate class, and a Dean to see whether a whole programme is behind the faculty."
)

st.markdown("#### Equity Review Group")
st.markdown(
    "A combined field of gender, NSFAS funding status and residence status, used only to surface patterns "
    "across these dimensions for equity monitoring. It is never used to make decisions about an individual "
    "student in isolation."
)

st.markdown("#### Pass mark")
st.markdown("A pass mark of 50 is used consistently to determine Failed_Assessment_Flag across all modules.")

render_footer()
