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
ADMIN_MOBILE = "7737684344"  # <--- THE ONLY NUMBER THAT SEES THE ADMIN BUTTON

# --- PAGE SETUP ---
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🇮🇳")

# --- CSS (Footer + Hiding Default Sidebar Elements) ---
st.markdown("""
    <style>
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
        z-index: 100;
    }
    .block-container { padding-bottom: 50px; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'reports' not in st.session_state: st.session_state.reports = []
if 'otp_verified' not in st.session_state: st.session_state.otp_verified = False
if 'otp_sent' not in st.session_state: st.session_state.otp_sent = False
if 'current_otp' not in st.session_state: st.session_state.current_otp = 0
if 'user_mobile' not in st.session_state: st.session_state.user_mobile = ""

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
    pdf.multi_cell(0, 10, txt=f"AI Reason: {ticket['reason']}")
    pdf.ln(20)
    pdf.cell(200, 10, txt="Authorized Signature: _______________________", ln=True)
    return pdf.output(dest='S').encode('latin-1')

def analyze_image_simulation(image_file):
    name = image_file.name.lower()
    if "pothole" in name: return "Major Asphalt Deterioration", "High", "Severity Level 4 crater; exposed aggregate base."
    elif "garbage" in name: return "Illegal Waste Accumulation", "Medium", "Mixed solid waste pile; vector breeding risk."
    elif "light" in name: return "Streetlight Infrastructure Failure", "Medium", "Pole luminaire broken; electrical safety hazard."
    elif "pipe" in name: return "Potable Water Main Rupture", "High", "Significant treated water loss; risk of erosion."
    else: return "Civic Anomaly Detected", "Low", "Non-critical issue; flagged for manual review."

# --- NAVIGATION LOGIC (THE MAGIC PART) ---
st.sidebar.image("https://img.icons8.com/fluency/96/bruj-khalifa.png", width=50)
st.sidebar.title(APP_NAME)

# Default Page is Citizen
page = "📱 Citizen Reporting"

# ONLY SHOW NAVIGATION IF USER IS THE ADMIN NUMBER
if st.session_state.otp_verified and st.session_state.user_mobile == ADMIN_MOBILE:
    st.sidebar.success("⚡ Administrator Access Granted")
    page = st.sidebar.radio("Navigate", ["📱 Citizen Reporting", "🚔 Admin Dashboard"])
else:
    # Regular users don't see any radio button, just the text
    st.sidebar.markdown("**Citizen Portal**")

st.sidebar.divider()
st.sidebar.caption("System Status: 🟢 Online")

# ================= VIEW 1: CITIZEN REPORTING =================
if page == "📱 Citizen Reporting":
    st.title(f"🇮🇳 {APP_NAME} - Citizen Portal")
    
    # 1. LOGIN SCREEN
    if not st.session_state.otp_verified:
        with st.container(border=True):
            st.subheader("🔐 Secure Verification")
            phone = st.text_input("Mobile Number (+91)", max_chars=10, help="Admins use 7737684344")
            
            if st.button("Request OTP"):
                if len(phone)==10:
                    st.session_state.user_mobile = phone  # Save number to check later
                    st.session_state.otp_sent = True
                    st.session_state.current_otp = random.randint(1000, 9999)
                    with st.spinner("Connecting to SMS Gateway..."): time.sleep(1)
                    st.toast(f"DEBUG: Your OTP is {st.session_state.current_otp}", icon="📲")
                    st.info(f"💡 Demo OTP: {st.session_state.current_otp}")
            
            if st.session_state.otp_sent:
                otp = st.text_input("Enter OTP", type="password")
                if st.button("Verify") or otp == str(st.session_state.current_otp):
                    if otp == str(st.session_state.current_otp):
                        st.session_state.otp_verified = True
                        st.rerun()
                    else:
                        st.error("Invalid OTP")
    
    # 2. REPORTING SCREEN
    else:
        st.success(f"✅ Verified User: +91-{st.session_state.user_mobile}")
        
        # Show special message for Admin
        if st.session_state.user_mobile == ADMIN_MOBILE:
            st.info("🔓 Admin privileges detected. Check the Sidebar to switch views.")
            
        if st.button("Logout"): 
            st.session_state.otp_verified=False
            st.session_state.user_mobile=""
            st.rerun()
            
        st.divider()
        
        with st.form("report_form", clear_on_submit=True):
            st.subheader("📸 Upload Evidence")
            uploaded_file = st.file_uploader("Upload Photo", type=['jpg','png','jpeg'])
            st.info(f"📍 GPS Locked: RV College of Engineering ({RVCE_LAT}, {RVCE_LON})")
            
            if st.form_submit_button("🚀 Submit Report"):
                if uploaded_file:
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress.progress(i+1)
                    cat, prio, reason = analyze_image_simulation(uploaded_file)
                    new_report = {
                        "id": f"TKT-{random.randint(10000, 99999)}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "category": cat, "priority": prio, "reason": reason,
                        "lat": RVCE_LAT, "lon": RVCE_LON, "status": "Open"
                    }
                    st.session_state.reports.append(new_report)
                    st.balloons()
                    st.success(f"Ticket #{new_report['id']} Created: {cat}")

# ================= VIEW 2: ADMIN DASHBOARD (RESTRICTED) =================
elif page == "🚔 Admin Dashboard":
    # Double Check Security (In case someone tries to hack the variable)
    if st.session_state.user_mobile != ADMIN_MOBILE:
        st.error("⛔ Unauthorized Access")
        st.stop()

    st.title("🚔 Triage Dashboard")
    st.metric("IoT Sensor Status", "8 Units Active", delta="Normal")
    
    if st.session_state.reports:
        df = pd.DataFrame(st.session_state.reports)
        
        # Action Panel
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            t_id = st.selectbox("Select Ticket to Manage", df['id'].tolist())
        
        selected_ticket = next((x for x in st.session_state.reports if x["id"] == t_id), None)
        
        with c2:
            if st.button("✅ Mark Resolved"):
                if selected_ticket:
                    selected_ticket['status'] = "Resolved"
                    st.toast("SMS Sent to Citizen: 'Issue Resolved'", icon="📨")
                    time.sleep(1); st.rerun()
        
        with c3:
            if selected_ticket:
                pdf_data = create_pdf(selected_ticket)
                st.download_button("⬇️ PDF Report", pdf_data, f"{t_id}.pdf", "application/pdf")

        # Data Table
        def color_row(row):
            return ['background-color: #ffcccb; color: black' if row['priority'] == 'High' else '' for _ in row]
        
        st.subheader("📋 Active Tickets")
        st.dataframe(df.style.apply(color_row, axis=1), use_container_width=True)
        
        # Visuals
        c1, c2 = st.columns(2)
        c1.map(df, zoom=15, color="#ff0000")
        c2.line_chart(pd.DataFrame(np.random.randint(60, 150, size=(20, 1)), columns=['AQI']))

    else:
        st.info("No tickets in the system yet. Submit one from the Citizen App!")

# --- COPYRIGHT FOOTER ---
st.markdown(
    """
    <div class="footer">
        <p>© 2026 Wanderers 5th Semester EL | All Rights Reserved</p>
    </div>
    """,
    unsafe_allow_html=True
)
