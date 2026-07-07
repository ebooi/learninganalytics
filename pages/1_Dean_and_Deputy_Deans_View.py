import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data_loader import load_module_data, load_programme_data, sidebar_filters
from utils.narrative import ai_toggle, generate_narrative
from utils.styling import (
    CHART_SEQUENCE,
    MID_GREY,
    RISK_COLOURS,
    UNIVERSITY_BLUE,
    UNIVERSITY_GOLD,
    apply_uwc_theme,
    render_footer,
    render_header,
)

st.set_page_config(page_title="Dean and Deputy Deans' View | LA_Practice_APP", page_icon="🎓", layout="wide")
apply_uwc_theme()
render_header(
    "Dean and Deputy Deans' View",
    "Faculty-wide progression, risk and equity picture, for strategic decision-making.",
)

prog_df = load_programme_data()
mod_df = load_module_data()
prog_f, mod_f, sel = sidebar_filters(prog_df, mod_df, key_prefix="dean")

if prog_f.empty:
    st.warning("No students match the current filter selection. Adjust the filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------
# Headline KPIs
# ---------------------------------------------------------------------
st.markdown("### Faculty headline indicators")

total_students = prog_f["STUDENT_NUMBER"].nunique()
risk_counts = prog_f["Progression_Risk_Level"].value_counts(normalize=True) * 100
avg_final = prog_f["Student_Final_Average"].mean()
avg_credit_completion = prog_f["Credit_Completion_ToDate_Pct"].mean() * 100
non_sub_rate = (mod_f["Non_Submission_Flag"] == "Yes").mean() * 100
fail_rate = (mod_f["Failed_Assessment_Flag"] == "Yes").mean() * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Students", f"{total_students:,}")
c2.metric("On track", f"{risk_counts.get('On Track', 0):.1f}%")
c3.metric("Watch", f"{risk_counts.get('Watch', 0):.1f}%")
c4.metric("High risk", f"{risk_counts.get('High Risk', 0):.1f}%")
c5.metric("Average final mark", f"{avg_final:.1f}")
c6.metric("Credit completion to date", f"{avg_credit_completion:.1f}%")

st.markdown("---")

# ---------------------------------------------------------------------
# Risk distribution by programme
# ---------------------------------------------------------------------
col_a, col_b = st.columns([1.3, 1])

with col_a:
    st.markdown("#### Risk profile by programme")
    risk_by_prog = (
        prog_f.groupby(["Programme_Name", "Progression_Risk_Level"])
        .size()
        .reset_index(name="Count")
    )
    totals = risk_by_prog.groupby("Programme_Name")["Count"].transform("sum")
    risk_by_prog["Share"] = risk_by_prog["Count"] / totals * 100

    fig = px.bar(
        risk_by_prog,
        x="Share",
        y="Programme_Name",
        color="Progression_Risk_Level",
        orientation="h",
        color_discrete_map=RISK_COLOURS,
        category_orders={"Progression_Risk_Level": ["On Track", "Watch", "High Risk"]},
        labels={"Share": "Share of students (%)", "Programme_Name": "", "Progression_Risk_Level": "Risk level"},
    )
    fig.update_layout(barmode="stack", legend_title_text="", height=380)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown("#### Average final mark vs faculty average")
    prog_avg = prog_f.groupby("Programme_Name", as_index=False)["Student_Final_Average"].mean()
    faculty_avg = prog_f["Student_Final_Average"].mean()

    fig2 = px.bar(
        prog_avg.sort_values("Student_Final_Average"),
        x="Student_Final_Average",
        y="Programme_Name",
        orientation="h",
        color_discrete_sequence=[UNIVERSITY_BLUE],
        labels={"Student_Final_Average": "Average final mark", "Programme_Name": ""},
    )
    fig2.add_vline(x=faculty_avg, line_dash="dash", line_color=UNIVERSITY_GOLD,
                    annotation_text=f"Faculty average: {faculty_avg:.1f}", annotation_position="top")
    fig2.update_layout(height=380)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Equity lens
# ---------------------------------------------------------------------
st.markdown("#### Equity lens: share of students at high risk")

equity_dims = {
    "Gender": "Gender",
    "NSFAS funded": "NSFAS_Flag",
    "Residence": "Residence_Flag",
    "First-generation": "First_Generation_Flag",
}

equity_cols = st.columns(len(equity_dims))
for col, (label, field) in zip(equity_cols, equity_dims.items()):
    with col:
        grp = (
            prog_f.assign(is_high_risk=prog_f["Progression_Risk_Level"] == "High Risk")
            .groupby(field)["is_high_risk"]
            .mean()
            .reset_index()
        )
        grp["is_high_risk"] *= 100
        fig3 = px.bar(
            grp,
            x=field,
            y="is_high_risk",
            color_discrete_sequence=[UNIVERSITY_BLUE],
            labels={"is_high_risk": "High risk (%)", field: label},
        )
        fig3.update_layout(height=280, showlegend=False, title=label, title_font_size=13)
        st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Early intervention effectiveness: Early vs End at-risk transition
# ---------------------------------------------------------------------
st.markdown("#### Early intervention effectiveness")
st.caption(
    "Every student is flagged as at risk or not at both the early and end monitoring points. "
    "Comparing the two shows whether early intervention is working."
)

def transition_label(row):
    if row["Early_At_Risk_Flag"] == "No" and row["End_At_Risk_Flag"] == "No":
        return "Never at risk"
    if row["Early_At_Risk_Flag"] == "Yes" and row["End_At_Risk_Flag"] == "No":
        return "Resolved after early intervention"
    if row["Early_At_Risk_Flag"] == "Yes" and row["End_At_Risk_Flag"] == "Yes":
        return "Persisting risk"
    return "Newly emerged risk"

transitions = prog_f.assign(Transition=prog_f.apply(transition_label, axis=1))
trans_counts = transitions["Transition"].value_counts().reset_index()
trans_counts.columns = ["Transition", "Count"]
order = ["Never at risk", "Resolved after early intervention", "Newly emerged risk", "Persisting risk"]
colour_map = {
    "Never at risk": UNIVERSITY_BLUE,
    "Resolved after early intervention": UNIVERSITY_GOLD,
    "Newly emerged risk": "#385ba3",
    "Persisting risk": MID_GREY,
}

col_t1, col_t2 = st.columns([1, 1.4])
with col_t1:
    st.dataframe(
        trans_counts.set_index("Transition").reindex(order).rename(columns={"Count": "Students"}),
        use_container_width=True,
    )
with col_t2:
    fig4 = px.bar(
        trans_counts,
        x="Transition",
        y="Count",
        color="Transition",
        color_discrete_map=colour_map,
        category_orders={"Transition": order},
    )
    fig4.update_layout(height=320, showlegend=False, xaxis_title="", yaxis_title="Students")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------------------
# Programme summary table
# ---------------------------------------------------------------------
st.markdown("#### Programme summary table")
summary = prog_f.groupby("Programme_Name").agg(
    Students=("STUDENT_NUMBER", "nunique"),
    Avg_Final_Mark=("Student_Final_Average", "mean"),
    Credit_Completion_ToDate_Pct=("Credit_Completion_ToDate_Pct", "mean"),
    High_Risk_Pct=("Progression_Risk_Level", lambda s: (s == "High Risk").mean() * 100),
    Failed_Modules_Avg=("Failed_Module_Count", "mean"),
).round(1)
summary["Credit_Completion_ToDate_Pct"] *= 100
st.dataframe(summary, use_container_width=True)

st.markdown("---")
st.markdown("### Narrative summary")
use_ai = ai_toggle("dean_ai_toggle")

top_programme_risk = summary["High_Risk_Pct"].idxmax() if not summary.empty else "N/A"
fallback = (
    f"Across {total_students:,} students in the current selection, "
    f"{risk_counts.get('High Risk', 0):.1f} per cent are classified as high risk and "
    f"{risk_counts.get('Watch', 0):.1f} per cent are on watch. "
    f"{top_programme_risk} carries the highest share of high-risk students at "
    f"{summary['High_Risk_Pct'].max():.1f} per cent, against a faculty average final mark of {avg_final:.1f}.\n\n"
    f"Of students who were at risk at the early monitoring point, "
    f"{(transitions['Transition'] == 'Resolved after early intervention').sum()} moved off risk by the end "
    f"of the assessment cycle, while {(transitions['Transition'] == 'Persisting risk').sum()} remained at risk "
    f"throughout. A further {(transitions['Transition'] == 'Newly emerged risk').sum()} students were not flagged "
    f"early but became at risk by the end, which points to a gap in early detection worth reviewing.\n\n"
    f"Recommended focus: prioritise faculty-level support for {top_programme_risk} and review whether current "
    f"early monitoring thresholds are catching students who go on to struggle later in the term."
)

stats = {
    "total_students": total_students,
    "high_risk_pct": round(risk_counts.get("High Risk", 0), 1),
    "watch_pct": round(risk_counts.get("Watch", 0), 1),
    "average_final_mark": round(avg_final, 1),
    "programme_with_highest_risk": top_programme_risk,
    "resolved_after_early_intervention": int((transitions["Transition"] == "Resolved after early intervention").sum()),
    "persisting_risk": int((transitions["Transition"] == "Persisting risk").sum()),
    "newly_emerged_risk": int((transitions["Transition"] == "Newly emerged risk").sum()),
}

narrative = generate_narrative("dean", stats, fallback, use_ai=use_ai)
st.markdown(f"<div class='uwc-callout'>{narrative}</div>", unsafe_allow_html=True)

render_footer()
