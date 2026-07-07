import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import MONITORING_ORDER, load_module_data, load_programme_data, sidebar_filters
from utils.narrative import ai_toggle, generate_narrative
from utils.styling import UNIVERSITY_BLUE, UNIVERSITY_GOLD, MID_GREY, apply_uwc_theme, render_footer, render_header

st.set_page_config(page_title="Lecturer View | LA_Practice_APP", page_icon="📘", layout="wide")
apply_uwc_theme()
render_header(
    "Lecturer View",
    "Module-level tracking of submissions, marks and class progress, for early and end-of-cycle action.",
)

prog_df = load_programme_data()
mod_df = load_module_data()
prog_f, mod_f, sel = sidebar_filters(prog_df, mod_df, include_module=False, include_monitoring=False, key_prefix="lec")

if mod_f.empty:
    st.warning("No records match the current filter selection. Adjust the filters in the sidebar.")
    st.stop()

st.markdown("### Select your module")
module_options = sorted(mod_f["Module_Name"].unique())
focus_module = st.selectbox("Module", module_options, key="lecturer_module_select")

module_df = mod_f[mod_f["Module_Name"] == focus_module].copy()
module_info = module_df.iloc[0]

info_cols = st.columns(4)
info_cols[0].metric("Module code", module_info["Module_Code"])
info_cols[1].metric("Credits", int(module_info["Module_Credits"]))
info_cols[2].metric("Gateway module", module_info["Gateway_Module_Flag"])
info_cols[3].metric("Students enrolled", module_df["STUDENT_NUMBER"].nunique())

st.markdown("---")

# ---------------------------------------------------------------------
# Class progress across the assessment cycle
# ---------------------------------------------------------------------
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown("#### Class average progress across the assessment cycle")
    progress = module_df.groupby("Monitoring_Point", as_index=False).agg(
        Class_Average=("Mark_For_Progress", "mean"),
        Programme_Average=("Programme_Average_Assessment", "mean"),
    )
    progress["Monitoring_Point"] = progress["Monitoring_Point"].astype("category")
    progress["Monitoring_Point"] = progress["Monitoring_Point"].cat.set_categories(MONITORING_ORDER, ordered=True)
    progress = progress.sort_values("Monitoring_Point")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=progress["Monitoring_Point"], y=progress["Class_Average"],
                              mode="lines+markers", name="Class average", line=dict(color=UNIVERSITY_BLUE, width=3)))
    fig.add_trace(go.Scatter(x=progress["Monitoring_Point"], y=progress["Programme_Average"],
                              mode="lines+markers", name="Programme average", line=dict(color=UNIVERSITY_GOLD, width=3, dash="dash")))
    fig.update_layout(height=360, yaxis_title="Average mark", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### Submission status by assessment")
    status_counts = module_df.groupby(["Assessment_Name", "Assessment_Status"]).size().reset_index(name="Count")
    fig_s = px.bar(
        status_counts, x="Assessment_Name", y="Count", color="Assessment_Status",
        color_discrete_map={"Submitted": UNIVERSITY_BLUE, "Late": UNIVERSITY_GOLD, "Not Submitted": MID_GREY},
    )
    fig_s.update_layout(height=360, xaxis_title="", legend_title_text="")
    st.plotly_chart(fig_s, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Latest monitoring point scatter: student mark vs class average
# ---------------------------------------------------------------------
st.markdown("#### Student marks vs class average at each monitoring point")
mp_pick = st.radio("Monitoring point", MONITORING_ORDER, horizontal=True, key="lecturer_mp_pick")
mp_df = module_df[module_df["Monitoring_Point"] == mp_pick]

if mp_df.empty:
    st.info("No assessments recorded for this module at the selected monitoring point.")
else:
    fig_sc = px.scatter(
        mp_df, x="STUDENT_NUMBER", y="Mark_For_Progress",
        color="Failed_Assessment_Flag",
        color_discrete_map={"Yes": MID_GREY, "No": UNIVERSITY_BLUE},
        labels={"Mark_For_Progress": "Mark", "STUDENT_NUMBER": "Student number", "Failed_Assessment_Flag": "Failed"},
    )
    class_avg_line = mp_df["Class_Average_Assessment"].mean()
    fig_sc.add_hline(y=class_avg_line, line_dash="dash", line_color=UNIVERSITY_GOLD,
                      annotation_text=f"Class average: {class_avg_line:.1f}")
    fig_sc.update_layout(height=380)
    st.plotly_chart(fig_sc, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Flagged students list
# ---------------------------------------------------------------------
st.markdown("#### Students needing contact")
flagged = module_df[
    (module_df["Non_Submission_Flag"] == "Yes")
    | (module_df["Failed_Assessment_Flag"] == "Yes")
    | (module_df["Early_Alert_Flag"] == "Yes")
][
    ["STUDENT_NUMBER", "Assessment_Name", "Monitoring_Point", "Assessment_Status",
     "Assessment_Mark", "Class_Average_Assessment", "Alert_Reason"]
].sort_values(["Monitoring_Point", "STUDENT_NUMBER"])

st.dataframe(flagged, use_container_width=True, height=300)
st.download_button(
    "Download contact list (CSV)",
    flagged.to_csv(index=False).encode("utf-8"),
    file_name=f"{module_info['Module_Code']}_students_needing_contact.csv",
    mime="text/csv",
)

st.markdown("---")

# ---------------------------------------------------------------------
# Individual student trajectory within this module
# ---------------------------------------------------------------------
st.markdown("#### Individual student trajectory in this module")
student_pick = st.selectbox(
    "Student number", sorted(module_df["STUDENT_NUMBER"].unique()), key="lecturer_student_pick"
)
student_traj = module_df[module_df["STUDENT_NUMBER"] == student_pick].sort_values("Assessment_Date")

fig_t = go.Figure()
fig_t.add_trace(go.Scatter(x=student_traj["Assessment_Name"], y=student_traj["Mark_For_Progress"],
                            mode="lines+markers", name="Student mark", line=dict(color=UNIVERSITY_BLUE, width=3)))
fig_t.add_trace(go.Scatter(x=student_traj["Assessment_Name"], y=student_traj["Class_Average_Assessment"],
                            mode="lines+markers", name="Class average", line=dict(color=UNIVERSITY_GOLD, width=2, dash="dash")))
fig_t.update_layout(height=340, yaxis_title="Mark")
st.plotly_chart(fig_t, use_container_width=True)

st.dataframe(
    student_traj[["Assessment_Name", "Monitoring_Point", "Assessment_Status", "Assessment_Mark",
                  "Class_Average_Assessment", "Difference_From_Class_Avg", "Alert_Reason"]],
    use_container_width=True,
)

st.markdown("---")
st.markdown("### Narrative summary")
use_ai = ai_toggle("lec_ai_toggle")

mp_class_avg = mp_df["Class_Average_Assessment"].mean() if not mp_df.empty else 0
gateway_note = (
    "a gateway module, so failure here affects progression directly"
    if module_info["Gateway_Module_Flag"] == "Yes"
    else "not a gateway module"
)
fallback = (
    f"In {focus_module}, {len(flagged['STUDENT_NUMBER'].unique())} of {module_df['STUDENT_NUMBER'].nunique()} "
    f"students currently show a non-submission, a failed assessment, or an active early alert. The class average "
    f"at the {mp_pick} monitoring point is {mp_class_avg:.1f}, and the module is {gateway_note}.\n\n"
    f"Priority for contact this week: students appearing in the list above with a non-submission flag, since these "
    f"carry the highest risk of falling further behind before the next monitoring point."
)

stats = {
    "module": focus_module,
    "students_flagged": len(flagged["STUDENT_NUMBER"].unique()) if not flagged.empty else 0,
    "total_students": module_df["STUDENT_NUMBER"].nunique(),
    "monitoring_point": mp_pick,
    "gateway_module": module_info["Gateway_Module_Flag"],
}

narrative = generate_narrative("lecturer", stats, fallback, use_ai=use_ai)
st.markdown(f"<div class='uwc-callout'>{narrative}</div>", unsafe_allow_html=True)

render_footer()
