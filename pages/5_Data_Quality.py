import pandas as pd
import streamlit as st

from utils.data_loader import load_module_data, load_programme_data
from utils.styling import UNIVERSITY_BLUE, apply_uwc_theme, render_footer, render_header

st.set_page_config(page_title="Data Quality | LA_Practice_APP", page_icon="🔍", layout="wide")
apply_uwc_theme()
render_header(
    "Data Quality",
    "Completeness, validity and consistency checks on the data behind this dashboard, run each time the app loads.",
)

prog_df = load_programme_data()
mod_df = load_module_data()

st.markdown(
    "These checks exist so that every stakeholder view can be trusted. Each check runs live against the "
    "current data files, so results reflect the data actually loaded, not a fixed report."
)

# ---------------------------------------------------------------------
# 1. Completeness
# ---------------------------------------------------------------------
st.markdown("### 1. Completeness")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Programme Tracking sheet**")
    completeness_prog = (1 - prog_df.isna().mean()) * 100
    st.dataframe(
        completeness_prog.round(2).rename("Complete (%)").to_frame(),
        use_container_width=True,
        height=280,
    )
with col2:
    st.markdown("**Student Module Level sheet**")
    completeness_mod = (1 - mod_df.isna().mean()) * 100
    st.dataframe(
        completeness_mod.round(2).rename("Complete (%)").to_frame(),
        use_container_width=True,
        height=280,
    )

overall_complete = (1 - pd.concat([prog_df.isna().mean(), mod_df.isna().mean()])).mean() * 100
st.metric("Overall completeness across both sheets", f"{overall_complete:.2f}%")

st.markdown("---")

# ---------------------------------------------------------------------
# 2. Uniqueness and duplicates
# ---------------------------------------------------------------------
st.markdown("### 2. Uniqueness")

dup_students = int(prog_df["STUDENT_NUMBER"].duplicated().sum())
dup_assessments = int(
    mod_df.duplicated(subset=["STUDENT_NUMBER", "Module_Code", "Assessment_ID"]).sum()
)

c1, c2 = st.columns(2)
c1.metric("Duplicate student records (Programme Tracking)", dup_students,
          delta="Pass" if dup_students == 0 else "Review needed", delta_color="off")
c2.metric("Duplicate assessment records (Student Module Level)", dup_assessments,
          delta="Pass" if dup_assessments == 0 else "Review needed", delta_color="off")

st.markdown("---")

# ---------------------------------------------------------------------
# 3. Validity: value ranges
# ---------------------------------------------------------------------
st.markdown("### 3. Validity")

mark_out_of_range = int(((mod_df["Assessment_Mark"] < 0) | (mod_df["Assessment_Mark"] > 100)).sum())
pct_cols = ["Credit_Completion_Current_Pct", "Credit_Completion_ToDate_Pct"]
pct_out_of_range = int(
    prog_df[pct_cols].apply(lambda s: ((s < 0) | (s > 1))).sum().sum()
)
neg_credits = int((prog_df["Total_Credits_Passed"] < 0).sum())

v1, v2, v3 = st.columns(3)
v1.metric("Assessment marks outside 0 to 100", mark_out_of_range,
          delta="Pass" if mark_out_of_range == 0 else "Review needed", delta_color="off")
v2.metric("Credit completion values outside 0 to 100%", pct_out_of_range,
          delta="Pass" if pct_out_of_range == 0 else "Review needed", delta_color="off")
v3.metric("Negative credit totals", neg_credits,
          delta="Pass" if neg_credits == 0 else "Review needed", delta_color="off")

st.markdown("---")

# ---------------------------------------------------------------------
# 4. Consistency between records and flags
# ---------------------------------------------------------------------
st.markdown("### 4. Consistency")

status_vs_flag = pd.crosstab(mod_df["Assessment_Status"], mod_df["Non_Submission_Flag"])
st.markdown("**Assessment status vs non-submission flag** (Not Submitted should align fully with a Yes flag)")
st.dataframe(status_vs_flag, use_container_width=True)

recon_ns = (
    mod_df.assign(is_ns=mod_df["Non_Submission_Flag"] == "Yes")
    .groupby("STUDENT_NUMBER")["is_ns"]
    .sum()
    .reset_index(name="module_level_count")
)
merged_ns = prog_df.merge(recon_ns, on="STUDENT_NUMBER")
mismatch_ns = int((merged_ns["module_level_count"] != merged_ns["Non_Submitted_Assessment_Count"]).sum())

recon_fail = (
    mod_df.assign(is_fail=mod_df["Failed_Assessment_Flag"] == "Yes")
    .groupby("STUDENT_NUMBER")["is_fail"]
    .sum()
    .reset_index(name="module_level_count")
)
merged_fail = prog_df.merge(recon_fail, on="STUDENT_NUMBER")
mismatch_fail = int((merged_fail["module_level_count"] != merged_fail["Failed_Assessment_Count"]).sum())

c1, c2 = st.columns(2)
c1.metric("Students where non-submission count reconciles", f"{len(merged_ns) - mismatch_ns} / {len(merged_ns)}",
          delta="Pass" if mismatch_ns == 0 else f"{mismatch_ns} mismatches", delta_color="off")
c2.metric("Students where failed assessment count reconciles", f"{len(merged_fail) - mismatch_fail} / {len(merged_fail)}",
          delta="Pass" if mismatch_fail == 0 else f"{mismatch_fail} mismatches", delta_color="off")

if mismatch_fail > 0:
    st.markdown(
        f"<div class='uwc-callout'>The programme-level <b>Failed_Assessment_Count</b> does not reconcile with "
        f"the module-level <b>Failed_Assessment_Flag</b> total for {mismatch_fail} students. This should be "
        f"traced to source before the failed-assessment count is used in any formal reporting.</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Show affected student numbers"):
        affected = merged_fail[merged_fail["module_level_count"] != merged_fail["Failed_Assessment_Count"]][
            ["STUDENT_NUMBER", "Failed_Assessment_Count", "module_level_count"]
        ].rename(columns={"module_level_count": "Recalculated_From_Module_Level"})
        st.dataframe(affected, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# 5. Freshness
# ---------------------------------------------------------------------
st.markdown("### 5. Freshness")
f1, f2, f3 = st.columns(3)
f1.metric("Earliest assessment date", str(mod_df["Assessment_Date"].min().date()))
f2.metric("Latest assessment date", str(mod_df["Assessment_Date"].max().date()))
f3.metric("Academic year(s) present", ", ".join(str(y) for y in sorted(prog_df["Academic_Year"].unique())))

st.markdown("---")
st.markdown("### Summary")
checks_passed = sum([
    dup_students == 0,
    dup_assessments == 0,
    mark_out_of_range == 0,
    pct_out_of_range == 0,
    neg_credits == 0,
    mismatch_ns == 0,
    mismatch_fail == 0,
])
st.markdown(
    f"<div class='uwc-callout'><b>{checks_passed} of 7 automated checks passed.</b> "
    f"Overall field completeness across both sheets is {overall_complete:.2f}%. "
    f"{'No outstanding issues were found.' if checks_passed == 7 else 'See the consistency section above for the item requiring follow-up.'}</div>",
    unsafe_allow_html=True,
)

render_footer()
