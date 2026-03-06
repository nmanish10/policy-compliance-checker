import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from report_generator import generate_pdf_report
from agent import ComplianceAgent
from evaluation import run_evaluation


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Policy Compliance Intelligence",
    layout="wide",
    page_icon="🛡️"
)

# ---------------------------------------------------
# DARK SaaS STYLING
# ---------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0F172A;
    color: #E5E7EB;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 46px;
    font-weight: 800;
    color: #FFFFFF;
}

.subtitle {
    font-size: 18px;
    color: #9CA3AF;
}

.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 30px;
}

hr {
    border: 1px solid #1E293B;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown('<div class="main-title">🛡️ Policy Compliance Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered structured compliance validation engine</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------------------------------
# AGENT INSTANCE
# ---------------------------------------------------

agent = ComplianceAgent()

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "📊 Compliance Analysis",
    "🧪 Benchmark Analytics",
    "🔄 Replay Runs"
])

# ===================================================
# TAB 1 – COMPLIANCE ANALYSIS
# ===================================================

with tab1:

    colA, colB = st.columns([3, 1])

    with colA:
        policy_input = st.text_area("Enter Policy Text", height=200)

    with colB:
        seed = st.number_input("Seed", value=42)
        run_clicked = st.button("Analyze Policy", use_container_width=True)

    # Run analysis
    if run_clicked:

        output = agent.run(policy_input, seed=seed)
        st.session_state["analysis"] = output

    # Display results if available
    if "analysis" in st.session_state:

        output = st.session_state["analysis"]

        if "error" in output:
            st.error(output["error"])
            st.stop()

        metrics = output["metrics"]
        result = output["result"]

        score = metrics["compliance_score"]
        risk = result["risk_level"]

        st.markdown("<hr>", unsafe_allow_html=True)

        # ---------------------------------------------------
        # COMPLIANCE GAUGE
        # ---------------------------------------------------

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Compliance Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#22C55E" if score > 75 else "#F59E0B" if score > 50 else "#EF4444"},
                'steps': [
                    {'range': [0, 50], 'color': "#1F2937"},
                    {'range': [50, 75], 'color': "#334155"},
                    {'range': [75, 100], 'color': "#475569"}
                ]
            }
        ))

        st.plotly_chart(gauge, use_container_width=True)

        # ---------------------------------------------------
        # METRICS
        # ---------------------------------------------------

        m1, m2, m3 = st.columns(3)

        m1.metric("Violations", metrics["violation_count"])
        m2.metric("Execution Time (ms)", metrics["execution_time_ms"])
        m3.metric("Risk Level", risk)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ---------------------------------------------------
        # SEVERITY DISTRIBUTION
        # ---------------------------------------------------

        severity_data = result["severity_breakdown"]

        if sum(severity_data.values()) > 0:

            donut = go.Figure(data=[go.Pie(
                labels=list(severity_data.keys()),
                values=list(severity_data.values()),
                hole=.6
            )])

            donut.update_layout(title="Violation Severity Distribution")

            st.plotly_chart(donut, use_container_width=True)

        else:
            st.success("No violations detected.")

        # ---------------------------------------------------
        # SUGGESTIONS
        # ---------------------------------------------------

        if output.get("suggestions"):

            st.markdown("### 💡 Policy Improvement Suggestions")

            for suggestion in output["suggestions"]:
                st.info(suggestion)

        # ---------------------------------------------------
        # PDF REPORT GENERATION
        # ---------------------------------------------------

        report_data = {
            "run_id": output["run_id"],
            "timestamp": output["timestamp"],
            "rule_version": result["rule_version"],
            "compliance_score": metrics["compliance_score"],
            "risk_level": result["risk_level"],
            "violations": result["violations"],
            "suggestions": output.get("suggestions", [])
        }

        pdf_path = "compliance_report.pdf"
        generate_pdf_report(report_data, pdf_path)

        with open(pdf_path, "rb") as f:

            st.download_button(
                label="📄 Download Compliance Report (PDF)",
                data=f,
                file_name="compliance_report.pdf",
                mime="application/pdf"
            )

        # ---------------------------------------------------
        # DEBUG / ADVANCED DETAILS
        # ---------------------------------------------------

        with st.expander("🔍 LLM Extracted Sections"):
            st.json(output["llm_output"])

        with st.expander("🧭 State Machine Trace"):
            st.json(output["state_history"])


# ===================================================
# TAB 2 – BENCHMARK ANALYTICS
# ===================================================

with tab2:

    if st.button("Run Benchmark Evaluation", use_container_width=True):

        evaluation = run_evaluation()

        results = evaluation["results"]
        critical_rate = evaluation["critical_detection_rate"]

        df = pd.DataFrame(results)

        avg_structured = df["structured_score"].mean()
        avg_baseline = df["baseline_score"].mean()
        overestimated = sum(df["baseline_score"] > df["structured_score"])

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Avg Structured Score", f"{round(avg_structured,2)}%")
        c2.metric("Avg Baseline Score", f"{round(avg_baseline,2)}%")
        c3.metric("Baseline Overestimation", f"{overestimated} cases")
        c4.metric("Critical Detection Rate", f"{critical_rate}%")

        st.markdown("<br>", unsafe_allow_html=True)

        fig = px.bar(
            df,
            x="scenario",
            y=["structured_score", "baseline_score"],
            barmode="group",
            title="Structured vs Baseline Comparison"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)


# ===================================================
# TAB 3 – REPLAY RUNS
# ===================================================

with tab3:

    if os.path.exists("runs"):

        run_files = sorted(
            os.listdir("runs"),
            key=lambda x: os.path.getmtime(f"runs/{x}"),
            reverse=True
        )

        if run_files:

            selected_run = st.selectbox("Select Run", run_files)

            if st.button("Load Run"):

                with open(f"runs/{selected_run}", "r") as f:
                    data = json.load(f)

                st.json(data)

        else:
            st.info("No stored runs yet.")

    else:
        st.info("Runs folder not found.")