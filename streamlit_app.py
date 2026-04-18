import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Add backend to path so we can import services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from services.assessment_builder import build_assessment
from services.assessment_history import get_assessment_history

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SmartISMS | Assessment Workspace",
    page_icon="🛡️",
    layout="wide",
)

# --- CUSTOM CSS (PREMIUM STYLE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .insight-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }
    
    .gap-box {
        background-color: #fef2f2;
        border: 1px solid #fee2e2;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        color: #991b1b;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_value=True)

# --- UI UTILS ---
def badge(text, color="blue"):
    colors = {
        "green": ("#dcfce7", "#166534"),
        "red": ("#fee2e2", "#991b1b"),
        "yellow": ("#fef9c3", "#854d0e"),
        "blue": ("#dbeafe", "#1e40af")
    }
    bg, fg = colors.get(color, colors["blue"])
    return f'<span style="background-color: {bg}; color: {fg}; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">{text}</span>'

# --- SESSION STATE ---
if 'assessment_data' not in st.session_state:
    st.session_state.assessment_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("SmartISMS")
    st.markdown("GRC & Compliance")
    st.divider()
    
    st.subheader("Assessment Controls")
    assessment_name = st.text_input("Entity Name", value="Global Corp")
    framework = st.selectbox("Compliance Standard", ["ISO 27001 (Enriched)", "NIST CSF", "PCI DSS"])
    
    st.divider()
    uploaded_file = st.file_uploader("Upload Evidence (Excel)", type=["xlsx", "xls"])
    
    if st.button("Execute Full Analysis", type="primary"):
        with st.spinner("Analyzing controls and mapping evidence..."):
            # If evidence exists, we process it. For now, we call build_assessment
            # If we wanted real mapping, we'd pass the uploaded file to the backend
            res = build_assessment(
                framework="iso27001",
                assessment_name=assessment_name
            )
            st.session_state.assessment_data = res
            st.success("Analysis Complete!")

# --- MAIN DASHBOARD ---
ad = st.session_state.assessment_data

if not ad:
    st.title("Compliance Workspace")
    st.info("Upload evidence and click 'Execute Full Analysis' to visualize results.")
    
    # Simple summary of previous runs
    st.subheader("Assessment History")
    history = get_assessment_history()
    if history:
        st.dataframe(pd.DataFrame(history)[['assessment_name', 'compliance_score', 'created_at']])
    else:
        st.write("No history found.")

else:
    # --- HEADER ---
    st.title(f"{ad['framework']} Compliance Report")
    st.markdown(f"**Entity:** {ad['assessment_name']} | **Status:** Evidence-Backed" if ad.get('evidence_backed') else f"**Entity:** {ad['assessment_name']} | **Status:** Baseline Only")
    
    # --- METRICS ---
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f'<div class="metric-card"><p style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase;">Score</p><h2 style="color:#2563eb; margin:0;">{ad["compliance_score"]}%</h2></div>', unsafe_allow_value=True)
    with m2:
        st.markdown(f'<div class="metric-card"><p style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase;">Controls</p><h2 style="color:#1e293b; margin:0;">{ad["total_controls"]}</h2></div>', unsafe_allow_value=True)
    with m3:
        st.markdown(f'<div class="metric-card"><p style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase;">Compliant</p><h2 style="color:#10b981; margin:0;">{ad["compliant_controls"]}</h2></div>', unsafe_allow_value=True)
    with m4:
        st.markdown(f'<div class="metric-card"><p style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase;">Partial</p><h2 style="color:#f59e0b; margin:0;">{ad.get("partial_controls", 0)}</h2></div>', unsafe_allow_value=True)
    with m5:
        st.markdown(f'<div class="metric-card"><p style="color:#64748b; font-size:0.7rem; font-weight:700; text-transform:uppercase;">Missing</p><h2 style="color:#ef4444; margin:0;">{ad["missing_controls"]}</h2></div>', unsafe_allow_value=True)

    # --- INSIGHTS & CHARTS ---
    st.write("")
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.subheader("🛠️ Smart Insights")
        for ins in ad.get('insights', []):
            st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_value=True)
            
    with col_right:
        st.subheader("📊 Severity Distribution")
        sev = ad.get('severity_summary', {})
        chart_data = []
        for s in ['high', 'medium', 'low']:
            s_data = sev.get(s, {})
            chart_data.append({"Severity": s.capitalize(), "Status": "Compliant", "Count": s_data.get('compliant', 0)})
            chart_data.append({"Severity": s.capitalize(), "Status": "Partial", "Count": s_data.get('partial', 0)})
            chart_data.append({"Severity": s.capitalize(), "Status": "Missing", "Count": s_data.get('missing', 0)})
        
        df_chart = pd.DataFrame(chart_data)
        fig = px.bar(df_chart, x="Severity", y="Count", color="Status", 
                     color_discrete_map={"Compliant": "#10B981", "Partial": "#F59E0B", "Missing": "#EF4444"},
                     barmode="stack", height=300)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        if ad.get('top_missing_high_risk'):
            st.subheader("⚠️ Critical Gaps")
            for gap in ad['top_missing_high_risk']:
                st.markdown(f'<div class="gap-box"><b>{gap["rule_id"]}</b>: {gap["name"]}</div>', unsafe_allow_value=True)

    # --- SECTION DETAILS ---
    st.markdown('<div class="section-header">Section Performance Breakdown</div>', unsafe_allow_value=True)
    
    for section in ad.get('sections', []):
        with st.expander(f"{section['section_key']} {section['section_name']} — {section['compliance_score']}% Compliant"):
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Compliant", section['compliant_controls'])
            sc2.metric("Partial", section.get('partial_controls', 0))
            sc3.metric("Missing", section['missing_controls'])
            
            # Table
            df_table = pd.DataFrame(section.get('controls', []))
            if not df_table.empty:
                st.dataframe(df_table[['rule_id', 'name', 'severity', 'status']], use_container_width=True)

st.divider()
st.caption("Auto-Sync: GitHub Repository smartisms-new-2")
