import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import MONITORING_ORDER, load_module_data, load_programme_data, sidebar_filters
from utils.narrative import ai_toggle, generate_narrative
from utils.styling import UNIVERSITY_BLUE, UNIVERSITY_GOLD, apply_uwc_theme, render_footer, render_header

st.set_page_config(page_title="Faculty Manager View | LA_Practice_APP", page_icon="🏛️", layout="wide")
apply_uwc_theme()
render_header(
    "Faculty Manager View",
    "Operational monitoring of modules and assessments, for coordination with lecturers and student support.",
)

prog_df = load_programme_data()
mod_df = load_module_data()
prog_f, mod_f, sel = sidebar_filters(prog_df, mod_df, include_module=True, include_monitoring=True, key_prefix="fm")

if mod_f.empty:
    st.warning("No records match the current filter selection. Adjust the filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------
st.markdown("### Operational indicators")

non_sub_rate = (mod_f["Non_Submission_Flag"] == "Yes").mean() * 100
fail_rate = (mod_f["Failed_Assessment_Flag"] == "Yes").mean() * 100
gateway_f = mod_f[mod_f["Gateway_Module_Flag"] == "Yes"]
gateway_fail_rate = (gateway_f["Failed_Assessment_Flag"] == "Yes").mean() * 100 if not gateway_f.empty else 0
alert_rate = (mod_f["Early_Alert_Flag"] == "Yes").mean() * 100
assessments_tracked = len(mod_f)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Assessment records", f"{assessments_tracked:,}")
c2.metric("Non-submission rate", f"{non_sub_rate:.1f}%")
c3.metric("Failed assessment rate", f"{fail_rate:.1f}%")
c4.metric("Gateway module failure rate", f"{gateway_fail_rate:.1f}%")
c5.metric("Flagged assessment records", f"{alert_rate:.1f}%")

st.markdown("---")

# ---------------------------------------------------------------------
# Heatmaps: module x monitoring point
# ---------------------------------------------------------------------
col_h1, col_h2 = st.columns(2)

with col_h1:
    st.markdown("#### Non-submission rate by module and monitoring point")
    heat1 = (
        mod_f.assign(is_ns=mod_f["Non_Submission_Flag"] == "Yes")
        .groupby(["Module_Name", "Monitoring_Point"])["is_ns"]
        .mean()
        .mul(100)
        .reset_index()
    )
    pivot1 = heat1.pivot(index="Module_Name", columns="Monitoring_Point", values="is_ns")
    pivot1 = pivot1.reindex(columns=[m for m in MONITORING_ORDER if m in pivot1.columns])
    fig1 = px.imshow(
        pivot1,
        text_auto=".1f",
        color_continuous_scale=[[0, "#faf6ed"], [0.5, "#bd9a50"], [1, "#0a1a5c"]],
        aspect="auto",
        labels=dict(color="Non-submission %"),
    )
    fig1.update_layout(height=420)
    st.plotly_chart(fig1, use_container_width=True)

with col_h2:
    st.markdown("#### Failed assessment rate by module and monitoring point")
    heat2 = (
        mod_f.assign(is_fail=mod_f["Failed_Assessment_Flag"] == "Yes")
        .groupby(["Module_Name", "Monitoring_Point"])["is_fail"]
        .mean()
        .mul(100)
        .reset_index()
    )
    pivot2 = heat2.pivot(index="Module_Name", columns="Monitoring_Point", values="is_fail")
    pivot2 = pivot2.reindex(columns=[m for m in MONITORING_ORDER if m in pivot2.columns])
    fig2 = px.imshow(
        pivot2,
        text_auto=".1f",
        color_continuous_scale=[[0, "#faf6ed"], [0.5, "#bd9a50"], [1, "#0a1a5c"]],
        aspect="auto",
        labels=dict(color="Failure %"),
    )
    fig2.update_layout(height=420)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Module average vs programme average
# ---------------------------------------------------------------------
st.markdown("#### Module average mark vs programme average")
module_avg = mod_f.groupby("Module_Name", as_index=False).agg(
    Class_Average=("Mark_For_Progress", "mean"),
    Programme_Average=("Programme_Average_Assessment", "mean"),
)
module_avg_melt = module_avg.melt(id_vars="Module_Name", var_name="Series", value_name="Average mark")
fig3 = px.bar(
    module_avg_melt,
    x="Module_Name",
    y="Average mark",
    color="Series",
    barmode="group",
    color_discrete_map={"Class_Average": UNIVERSITY_BLUE, "Programme_Average": UNIVERSITY_GOLD},
)
fig3.update_layout(height=380, xaxis_title="", legend_title_text="")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Gateway vs non-gateway comparison
# ---------------------------------------------------------------------
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("#### Gateway vs non-gateway module performance")
    gw = mod_f.groupby("Gateway_Module_Flag", as_index=False)["Mark_For_Progress"].mean()
    fig4 = px.bar(
        gw, x="Gateway_Module_Flag", y="Mark_For_Progress",
        color_discrete_sequence=[UNIVERSITY_BLUE],
        labels={"Gateway_Module_Flag": "Gateway module", "Mark_For_Progress": "Average mark"},
    )
    fig4.update_layout(height=340, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

with col_g2:
    st.markdown("#### Distribution of marks by monitoring point")
    fig5 = px.box(
        mod_f, x="Monitoring_Point", y="Mark_For_Progress",
        category_orders={"Monitoring_Point": MONITORING_ORDER},
        color_discrete_sequence=[UNIVERSITY_BLUE],
    )
    fig5.update_layout(height=340, xaxis_title="", yaxis_title="Mark")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# At-risk list, downloadable
# ---------------------------------------------------------------------
st.markdown("#### At-risk assessment list")
st.caption("Students with non-submission, failed assessment, or an active early alert in the current selection.")

at_risk = mod_f[
    (mod_f["Non_Submission_Flag"] == "Yes")
    | (mod_f["Failed_Assessment_Flag"] == "Yes")
    | (mod_f["Early_Alert_Flag"] == "Yes")
][
    [
        "STUDENT_NUMBER", "Programme_Name", "Module_Name", "Assessment_Name", "Monitoring_Point",
        "Assessment_Status", "Assessment_Mark", "Class_Average_Assessment", "Alert_Reason",
    ]
].sort_values(["Module_Name", "Monitoring_Point"])

st.dataframe(at_risk, use_container_width=True, height=320)
st.download_button(
    "Download at-risk list (CSV)",
    at_risk.to_csv(index=False).encode("utf-8"),
    file_name="faculty_manager_at_risk_list.csv",
    mime="text/csv",
)

st.markdown("---")
st.markdown("### Narrative summary")
use_ai = ai_toggle("fm_ai_toggle")

worst_module_ns = pivot1.mean(axis=1).idxmax() if not pivot1.empty else "N/A"
worst_module_fail = pivot2.mean(axis=1).idxmax() if not pivot2.empty else "N/A"

fallback = (
    f"Across the current selection there are {assessments_tracked:,} assessment records, with a non-submission "
    f"rate of {non_sub_rate:.1f} per cent and a failed assessment rate of {fail_rate:.1f} per cent. Gateway modules "
    f"show a failure rate of {gateway_fail_rate:.1f} per cent, which warrants close monitoring given their effect "
    f"on progression.\n\n"
    f"{worst_module_ns} has the highest average non-submission rate across monitoring points, while {worst_module_fail} "
    f"has the highest average failure rate. The at-risk list below lists {len(at_risk):,} records that need lecturer "
    f"or student support follow-up, and can be downloaded for outreach coordination this week."
)

stats = {
    "assessment_records": assessments_tracked,
    "non_submission_rate": round(non_sub_rate, 1),
    "failed_assessment_rate": round(fail_rate, 1),
    "gateway_failure_rate": round(gateway_fail_rate, 1),
    "module_with_highest_non_submission": worst_module_ns,
    "module_with_highest_failure": worst_module_fail,
    "at_risk_records": len(at_risk),
}

narrative = generate_narrative("faculty_manager", stats, fallback, use_ai=use_ai)
st.markdown(f"<div class='uwc-callout'>{narrative}</div>", unsafe_allow_html=True)

render_footer()
