import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import MONITORING_ORDER, load_module_data, load_programme_data
from utils.narrative import ai_toggle, generate_narrative
from utils.styling import (
    MID_GREY,
    UNIVERSITY_BLUE,
    UNIVERSITY_GOLD,
    apply_uwc_theme,
    render_footer,
    render_header,
    risk_badge,
)

st.set_page_config(page_title="Student View | LA_Practice_APP", page_icon="🧑‍🎓", layout="wide")
apply_uwc_theme()
render_header(
    "Student View",
    "A personal dashboard comparing your progress with your class and programme.",
)

prog_df = load_programme_data()
mod_df = load_module_data()

st.sidebar.markdown("## Find a student")
student_number = st.sidebar.selectbox(
    "Student number", sorted(prog_df["STUDENT_NUMBER"].unique()), key="student_pick"
)

student_row = prog_df[prog_df["STUDENT_NUMBER"] == student_number].iloc[0]
student_modules = mod_df[mod_df["STUDENT_NUMBER"] == student_number].copy()

# ---------------------------------------------------------------------
# Profile summary
# ---------------------------------------------------------------------
st.markdown(
    f"### {student_row['Programme_Name']} &middot; Year {int(student_row['Year_Level'])} "
    f"&middot; {risk_badge(student_row['Progression_Risk_Level'])}",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "My overall average",
    f"{student_row['Student_Final_Average']:.1f}",
    delta=f"{student_row['Difference_From_Programme_Avg']:.1f} vs programme",
)
c2.metric("Programme average", f"{student_row['Programme_Final_Average']:.1f}")
c3.metric("Credit completion to date", f"{student_row['Credit_Completion_ToDate_Pct'] * 100:.0f}%")
c4.metric("Modules not yet passed", f"{int(student_row['Failed_Module_Count'])}")

st.progress(min(max(student_row["Credit_Completion_ToDate_Pct"], 0.0), 1.0))

st.markdown(
    f"<div class='uwc-callout'><b>Recommended next step:</b> {student_row['Recommended_Action']}</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------------------------------------------------------------
# Module-by-module progress
# ---------------------------------------------------------------------
st.markdown("#### My progress by module")

module_choice = st.selectbox(
    "Module", sorted(student_modules["Module_Name"].unique()), key="student_module_pick"
)
one_module = student_modules[student_modules["Module_Name"] == module_choice].sort_values("Assessment_Date")

col1, col2 = st.columns([1.4, 1])

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=one_module["Assessment_Name"], y=one_module["Mark_For_Progress"],
        mode="lines+markers", name="My mark", line=dict(color=UNIVERSITY_BLUE, width=3),
    ))
    fig.add_trace(go.Scatter(
        x=one_module["Assessment_Name"], y=one_module["Class_Average_Assessment"],
        mode="lines+markers", name="Class average", line=dict(color=UNIVERSITY_GOLD, width=2, dash="dash"),
    ))
    fig.add_trace(go.Scatter(
        x=one_module["Assessment_Name"], y=one_module["Programme_Average_Assessment"],
        mode="lines+markers", name="Programme average", line=dict(color=MID_GREY, width=2, dash="dot"),
    ))
    fig.update_layout(height=380, yaxis_title="Mark", title=module_choice)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("##### Assessment record")
    st.dataframe(
        one_module[["Assessment_Name", "Monitoring_Point", "Assessment_Status", "Assessment_Mark",
                     "Class_Average_Assessment", "Difference_From_Class_Avg"]].set_index("Assessment_Name"),
        use_container_width=True,
        height=340,
    )

st.markdown("---")

# ---------------------------------------------------------------------
# All modules overview
# ---------------------------------------------------------------------
st.markdown("#### All my modules this year")
module_summary = student_modules.groupby("Module_Name", as_index=False).agg(
    My_Average=("Mark_For_Progress", "mean"),
    Class_Average=("Class_Average_Assessment", "mean"),
    Programme_Average=("Programme_Average_Assessment", "mean"),
    Non_Submissions=("Non_Submission_Flag", lambda s: (s == "Yes").sum()),
    Failed_Assessments=("Failed_Assessment_Flag", lambda s: (s == "Yes").sum()),
).round(1)

fig_all = px.bar(
    module_summary.melt(id_vars="Module_Name", value_vars=["My_Average", "Class_Average", "Programme_Average"],
                         var_name="Series", value_name="Average mark"),
    x="Module_Name", y="Average mark", color="Series", barmode="group",
    color_discrete_map={"My_Average": UNIVERSITY_BLUE, "Class_Average": UNIVERSITY_GOLD, "Programme_Average": MID_GREY},
)
fig_all.update_layout(height=380, xaxis_title="", legend_title_text="")
st.plotly_chart(fig_all, use_container_width=True)

st.dataframe(module_summary.set_index("Module_Name"), use_container_width=True)

st.markdown("---")
st.markdown("### A note on where you stand")
use_ai = ai_toggle("student_ai_toggle")

direction = "above" if student_row["Difference_From_Programme_Avg"] >= 0 else "below"
fallback = (
    f"Your overall average this year is {student_row['Student_Final_Average']:.1f}, which is "
    f"{abs(student_row['Difference_From_Programme_Avg']):.1f} marks {direction} the programme average of "
    f"{student_row['Programme_Final_Average']:.1f}. You have completed {student_row['Credit_Completion_ToDate_Pct'] * 100:.0f} "
    f"per cent of the credits expected so far this year.\n\n"
    f"Next step: {student_row['Recommended_Action']}. Reach out to your lecturer or the student success office if "
    f"you would like support putting this into action."
)

stats = {
    "overall_average": round(student_row["Student_Final_Average"], 1),
    "programme_average": round(student_row["Programme_Final_Average"], 1),
    "difference_from_programme_average": round(student_row["Difference_From_Programme_Avg"], 1),
    "credit_completion_to_date_pct": round(student_row["Credit_Completion_ToDate_Pct"] * 100, 0),
    "risk_level": student_row["Progression_Risk_Level"],
    "recommended_action": student_row["Recommended_Action"],
}

narrative = generate_narrative("student", stats, fallback, use_ai=use_ai)
st.markdown(f"<div class='uwc-callout'>{narrative}</div>", unsafe_allow_html=True)

render_footer()
