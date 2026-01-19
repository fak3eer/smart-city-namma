import streamlit as st
import pandas as pd
import time
import random
import numpy as np
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURATION ---
RVCE_LAT = 12.9240
RVCE_LON = 77.4990
APP_NAME = "Namma Report"

# --- PAGE CONFIG & CSS (HIDING SIDEBAR & ADDING FOOTER) ---
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🇮🇳")

# CSS to hide default Streamlit elements and add Footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;} /* Hides the sidebar completely */
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117;
        color: #808495;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #262730;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'reports' not in st.session_state: st.session_state.reports = []
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'otp_verified' not in st.session_state: st.session_state.otp_verified = False
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'current_otp' not in st.session_state: st.session_state.current_otp = 0

# --- HELPER FUNCTIONS ---
def create_pdf(ticket):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"BBMP / RVCE Smart City Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Incident Report: #{ticket['id']}", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {ticket['timestamp']}", ln=True)
    pdf.cell(200, 10, txt=f"Category: {ticket['category']}", ln=True)
    pdf.cell(200, 10, txt=f"Priority: {ticket['priority']}", ln=True)
    pdf.cell(200, 10, txt=f"Status: {ticket['status']}", ln=True)
    pdf.ln(20)
    pdf.cell(200, 10, txt="Authorized Signature: _______________________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def analyze_image_simulation(image_file):
    name = image_file.name.lower()
    if "pothole" in name: return "Major Asphalt Deterioration", "High", "Severity Level 4 crater."
    elif "garbage" in name: return "Illegal Waste Accumulation", "Medium", "Health hazard detected."
    elif "light" in name: return "Streetlight Failure", "Medium", "Visibility issue."
    elif "pipe" in name: return "Water Main Rupture", "High", "Significant water loss."
    else: return "Civic Anomaly", "Low", "Manual inspection required."

# --- ROUTING LOGIC ---
# We check the URL query params to decide which page to show
# pesu.in -> Client
# pesu.in/?mode=admin -> Dashboard

query_params = st.query_params
mode = query_params.get("mode", "citizen")

# ================= VIEW 1: CITIZEN APP (Default) =================
if mode != "admin":
    st.image("https://img.icons8.com/fluency/96/bruj-khalifa.png", width=60)
    st.title(f"{APP_NAME}")
    st.markdown("#### Rapid Civic Issue Reporting System")
    
    if not st.session_state.otp_verified:
        with st.container(border=True):
            st.subheader("🔐 Login")
            phone = st.text_input("Mobile Number (+91)", max_chars=10)
            if st.button("Get OTP"):
                if len(phone)==10:
                    st.session_state.otp_sent = True
                    st.session_state.current_otp = random.randint(1000, 9999)
                    with st.spinner("Sending OTP..."): time.sleep(1)
                    st.toast(f"OTP: {st.session_state.current_otp}", icon="💬")
            if st.session_state.otp_sent:
                if st.button("Verify") or st.text_input("OTP", type="password") == str(st.session_state.current_otp):
                    st.session_state.otp_verified = True
                    st.rerun()
    else:
        st.success("✅ Verified Citizen")
        if st.button("Logout"): st.session_state.otp_verified=False; st.rerun()
        st.divider()
        with st.form("report"):
            st.subheader("📸 New Report")
            f = st.file_uploader("Upload Photo", type=['jpg','png'])
            st.caption(f"📍 Location: {RVCE_LAT}, {RVCE_LON}")
            if st.form_submit_button("Submit"):
                if f:
                    with st.spinner("Analyzing..."):
                        time.sleep(1.5)
                        cat, prio, reason = analyze_image_simulation(f)
                    new_report = {
                        "id": f"TKT-{random.randint(10000, 99999)}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "category": cat, "priority": prio, "reason": reason,
                        "lat": RVCE_LAT, "lon": RVCE_LON, "status": "Open"
                    }
                    st.session_state.reports.append(new_report)
                    st.balloons()
                    st.success(f"Reported: {cat}")

# ================= VIEW 2: ADMIN DASHBOARD (Hidden) =================
else:
    if not st.session_state.logged_in:
        st.title("🔒 Admin Portal")
        user = st.text_input("ID"); pwd = st.text_input("Password", type="password")
        if st.button("Login") and user=="admin" and pwd=="admin":
            st.session_state.logged_in = True; st.rerun()
    else:
        st.title("🚔 Triage Dashboard")
        st.metric("Live IoT Sensors", "8 Units Online", delta="Active")
        
        if st.session_state.reports:
            df = pd.DataFrame(st.session_state.reports)
            
            # Action Panel
            c1, c2 = st.columns(2)
            with c1:
                t_id = st.selectbox("Select Ticket", df['id'].tolist())
            with c2:
                if st.button("Mark Resolved"):
                    for t in st.session_state.reports:
                        if t['id'] == t_id: t['status'] = "Resolved"
                    st.success("Updated!"); st.toast("SMS Sent to User", icon="📨"); time.sleep(1); st.rerun()

            # PDF Download
            sel_ticket = next((x for x in st.session_state.reports if x["id"] == t_id), None)
            if sel_ticket:
                pdf_data = create_pdf(sel_ticket)
                st.download_button("⬇️ Download PDF", pdf_data, f"{t_id}.pdf", "application/pdf")

            # Data Table
            def color_row(row):
                return ['background-color: #ffcccb; color: black' if row['priority'] == 'High' else '' for _ in row]
            st.dataframe(df.style.apply(color_row, axis=1), use_container_width=True)
            
            # Graphs
            c1, c2 = st.columns(2)
            c1.map(df, zoom=15, color="#ff0000")
            c1.caption("Incident Heatmap")
            
            chart_data = pd.DataFrame(np.random.randint(60, 150, size=(20, 1)), columns=['AQI'])
            c2.line_chart(chart_data)
            c2.caption("Live Air Quality Sensor (RVCE)")

# --- COPYRIGHT FOOTER ---
st.markdown(
    """
    <div class="footer">
        <p>© 2026 Wanderers 5th Semester EL | All Rights Reserved</p>
    </div>
    """,
    unsafe_allow_html=True
)