import streamlit as st
import requests
import time
import os
import pandas as pd

st.set_page_config(
    page_title="AFC-CAE Audit Engine Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .reportview-container { background: #F8F9FA; }
        .metric-card {
            background-color: #FFFFFF;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 5px solid #D04A02;
            margin-bottom: 15px;
        }
        .status-header {
            padding: 15px;
            border-radius: 6px;
            color: #FFFFFF;
            font-weight: bold;
            margin-bottom: 25px;
        }
    </style>
""", unsafe_allow_html=True)

BACKEND_HOST = os.getenv("FASTAPI_BACKEND_URL", "http://127.0.0.1:8000")
INGEST_ENDPOINT = f"{BACKEND_HOST}/api/v1/audit/ingest"
STATUS_ENDPOINT_TEMPLATE = f"{BACKEND_HOST}/api/v1/audit/status/{{run_id}}"

if "run_id" not in st.session_state:
    st.session_state.run_id = None
if "audit_data" not in st.session_state:
    st.session_state.audit_data = None
if "polling_active" not in st.session_state:
    st.session_state.polling_active = False

st.sidebar.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/128/external-audit-business-and-finance-flatart-icons-flat-flatarticons.png", width=65)
st.sidebar.title("AFC-CAE Control Center")
st.sidebar.caption("Continuous Auditing Engine UI v1.1")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Ingest Loan Population Ledger",
    type=["csv", "parquet"],
    help="Upload official LendingClub ledger subsets (.csv or .parquet)"
)

trigger_audit = st.sidebar.button("Execute Population Audit", use_container_width=True, type="primary")

if trigger_audit and uploaded_file is not None:
    with st.spinner("Streaming data to Ingestion Gate..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(INGEST_ENDPOINT, files=files)

            if response.status_code == 202:
                res_json = response.json()
                st.session_state.run_id = res_json.get("run_id")
                st.session_state.polling_active = True
                st.session_state.audit_data = None
                st.sidebar.success(f"Ingested! Run ID: {st.session_state.run_id}")
            else:
                st.sidebar.error(f"Ingestion Rejected: {response.text}")
        except Exception as e:
            st.sidebar.error(f"Network Failure Connecting to Backend Engine: {str(e)}")

if st.session_state.polling_active and st.session_state.run_id:
    status_box = st.empty()
    progress_bar = st.progress(0)

    for percent_complete in range(1, 101, 5):
        try:
            status_url = STATUS_ENDPOINT_TEMPLATE.format(run_id=st.session_state.run_id)
            poll_resp = requests.get(status_url).json()
            current_status = poll_resp.get("status")

            if current_status == "SELESAI":
                st.session_state.audit_data = poll_resp.get("results")
                st.session_state.polling_active = False
                status_box.empty()
                progress_bar.empty()
                break
            elif current_status == "ERROR":
                st.session_state.polling_active = False
                status_box.error(f"Audit Worker Exception: {poll_resp.get('reason')}")
                progress_bar.empty()
                break
            else:
                status_box.info("⏳ Processing data stack at worker level. Evaluating full population...")
                progress_bar.progress(percent_complete)
                time.sleep(2.0)
        except Exception as e:
            st.session_state.polling_active = False
            status_box.error(f"Polling Registry Broken: {str(e)}")
            break

st.title("🛡️ AFC-CAE Continuous Auditing & Controls Dashboard")
st.markdown("Automated Detective Controls Matrix & High-Dimensional Risk Ingestion Ecosystem.")
st.markdown("---")

if st.session_state.audit_data:
    results = st.session_state.audit_data
    routing = results.get("risk_decision_routing", {})
    scenario = routing.get("scenario", "A")

    if scenario == "A":
        bg_color, badge_text = "#2E7D32", "SKENARIO A: PROCEED | Varians Kesalahan Operasional Normal (< 0.5%)"
    elif scenario == "B":
        bg_color, badge_text = "#EF6C00", "SKENARIO B: QUARANTINE & INVESTIGATE | Zona Pantau Terdeteksi (0.5% - 5%)"
    else:
        bg_color = "#C62828"
        badge_text = "⚠️ SKENARIO C: EMERGENCY HALT | Kontaminasi Sistemik Masif (> 5%)"

    st.markdown(f"""
        <div class='status-header' style='background-color: {bg_color};'>
            {badge_text} <br>
            <span style='font-weight: 300; font-size: 0.9em;'>System Guidance: {routing.get('description')}</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class='metric-card'>
            <small style='color: #666;'>Composite Anomaly Rate</small><br>
            <b style='font-size: 1.8em; color: {bg_color};'>{routing.get('composite_anomaly_rate_pct')}%</b>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card'>
            <small style='color: #666;'>Ledger Rows Evaluated</small><br>
            <b style='font-size: 1.8em; color: #1C1C1C;'>{routing.get('total_records_evaluated'):,} rows</b>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='metric-card'>
            <small style='color: #666;'>Deterministic Rule Breaches</small><br>
            <b style='font-size: 1.8em; color: #1C1C1C;'>{results.get('rbae_assertions', {}).get('aggregate_rule_failures', 0):,} flags</b>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='metric-card'>
            <small style='color: #666;'>Isolation Forest Anomalies</small><br>
            <b style='font-size: 1.8em; color: #1C1C1C;'>{results.get('ai_anomaly_metrics', {}).get('ai_flagged_count', 0):,} rows</b>
        </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "📊 Governance & Null Architecture",
        "🔍 Deterministic Assertion Logs (RBAE)",
        "🧠 Machine Learning & Forensics Proof (XAI)"
    ])

    with tab1:
        st.subheader("Null Architecture Structural Logs")
        null_logs = results.get("null_governance_logs", {})

        g_col1, g_col2, g_col3 = st.columns(3)
        g_col1.metric("Validated Policy Nulls (PDAN)", f"{len(null_logs.get('PDAN_assertions', []))} Columns")
        g_col2.metric("Un-Compensated Gaps (UCG)", f"{len(null_logs.get('UCG_findings', []))} Findings")
        g_col3.metric("Pre-Activation Inclusions (FEN)", f"{len(null_logs.get('FEN_violations', []))} Rows")

        if len(null_logs.get("PDAN_assertions", [])) > 0:
            st.markdown("**Confirmed PDAN Verifications:**")
            st.dataframe(pd.DataFrame(null_logs.get("PDAN_assertions")), use_container_width=True)

    with tab2:
        st.subheader("Rule Execution Metrics Summary")
        st.json(results.get("rbae_assertions"))

    with tab3:
        st.subheader("Explainable AI (XAI) Forensics Audit Trail")
        ai_metrics = results.get("ai_anomaly_metrics", {})

        st.markdown("#### High-Dimensional Outlier Root-Cause Proofs")
        xai_samples = ai_metrics.get("sample_xai_explanations", {})
        if xai_samples:
            for rec_id, xai_data in xai_samples.items():
                with st.expander(f"🛡️ Audit Proof Link: High Risk Row ID [ {rec_id} ]"):
                    ctx = xai_data.get("segment_context", {})
                    st.caption(f"**Cluster Coordinates:** Grade Segment {ctx.get('grade')} | Term Window {ctx.get('term')}")
                    st.write(f"**Top Anomaly Drivers Matrix:** `{xai_data.get('top_3_anomaly_drivers')}`")

                    dev_profile = xai_data.get("deviation_profile", {})
                    if dev_profile:
                        st.dataframe(pd.DataFrame(dev_profile).T, use_container_width=True)
        else:
            st.info("No records violated high-dimensional feature bounds in this transaction ledger.")
else:
    st.info("👋 System Idle. Please load a transaction ledger subset in the control center to start automated audit analysis.")
