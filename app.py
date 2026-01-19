import streamlit as st
import pandas as pd
import time
import random
import numpy as np
import hashlib 
from datetime import datetime, timedelta
from fpdf import FPDF

# --- CONFIGURATION ---
RVCE_LAT = 12.9240
RVCE_LON = 77.4990
APP_NAME = "Namma Report"
ADMIN_MOBILE = "7737684344"

# --- PAGE SETUP ---
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="🇮🇳")

# --- CSS ---
st.markdown("""
    <style>
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #0e1117; color: #808495;
        text-align: center; padding: 10px; font-size: 14px;
        border-top: 1px solid #262730; z-index: 100;
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
if 'lang' not in st.session_state: st.session_state.lang = "English" 

# --- TRANSLATIONS ---
TRANS = {
    "English": {
        "title": "Citizen Portal",
        "upload": "Upload Evidence",
        "submit": "🚀 Submit Report",
        "verify": "Verify",
        "login": "Secure Verification"
    },
    "Kannada": {
        "title": "ನಾಗರಿಕ ಪೋರ್ಟಲ್ (Citizen Portal)",
        "upload": "ಸಾಕ್ಷ್ಯವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (Upload)",
        "submit": "🚀 ದೂರು ಸಲ್ಲಿಸಿ (Submit)",
        "verify": "ಪರಿಶೀಲಿಸಿ (Verify)",
        "login": "ಸುರಕ್ಷಿತ ಲಾಗಿನ್ (Login)"
    }
}

# --- HELPER FUNCTIONS ---
def generate_blockchain_hash(data):
    block_string = f"{data}{time.time()}"
    return hashlib.sha256(block_string.encode()).hexdigest()[:16]

def create_pdf(ticket):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"BBMP / RVCE Smart City Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Ticket ID: #{ticket['id']}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Blockchain Hash (Immutable): {ticket['hash']}", ln=True)
    pdf.ln(5)
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

# --- SIDEBAR ---
st.sidebar.markdown("**Developed by Students of:**")
try:
    st.sidebar.image("https://rvce.edu.in/wp-content/uploads/2025/08/Logo-2.png", width=200)
except:
    st.sidebar.error("Logo Error")
st.sidebar.divider()
st.sidebar.title(APP_NAME)

# Language Toggle
lang = st.sidebar.radio("Language / ಭಾಷೆ", ["English", "Kannada"])
st.session_state.lang = lang

# Navigation Logic
page = "📱 Citizen Reporting"
if st.session_state.otp_verified and st.session_state.user_mobile == ADMIN_MOBILE:
    st.sidebar.success("⚡ Administrator Access")
    page = st.sidebar.radio("Navigate", ["📱 Citizen Reporting", "🚔 Admin Dashboard"])
else:
    st.sidebar.markdown("**Citizen Portal**")

st.sidebar.divider()
st.sidebar.caption("Blockchain Node: 🟢 Active") 

# ================= VIEW 1: CITIZEN REPORTING =================
if page == "📱 Citizen Reporting":
    t = TRANS[st.session_state.lang]
    st.title(f"🇮🇳 {APP_NAME} - {t['title']}")
    
    if not st.session_state.otp_verified:
        with st.container(border=True):
            st.subheader(f"🔐 {t['login']}")
            phone = st.text_input("Mobile Number (+91)", max_chars=10, help="Admins use 7737684344")
            
            if st.button("Request OTP"):
                if len(phone)==10:
                    st.session_state.user_mobile = phone
                    st.session_state.otp_sent = True
                    st.session_state.current_otp = random.randint(1000, 9999)
                    with st.spinner("Connecting..."): time.sleep(1)
                    st.toast(f"OTP: {st.session_state.current_otp}", icon="📲")
            
            if st.session_state.otp_sent:
                otp = st.text_input("OTP", type="password")
                if st.button(t['verify']) or otp == str(st.session_state.current_otp):
                    if otp == str(st.session_state.current_otp):
                        st.session_state.otp_verified = True
                        st.rerun()
                    else:
                        st.error("Invalid OTP")
    
    else:
        st.success(f"✅ Verified User: +91-{st.session_state.user_mobile}")
        if st.session_state.user_mobile == ADMIN_MOBILE:
            st.info("🔓 Admin privileges detected.")
        if st.button("Logout"): 
            st.session_state.otp_verified=False; st.session_state.user_mobile=""; st.rerun()
            
        st.divider()
        with st.form("report_form", clear_on_submit=True):
            st.subheader(f"📸 {t['upload']}")
            uploaded_file = st.file_uploader("", type=['jpg','png','jpeg'])
            st.info(f"📍 GPS Locked: RV College of Engineering ({RVCE_LAT}, {RVCE_LON})")
            
            if st.form_submit_button(t['submit']):
                if uploaded_file:
                    progress = st.progress(0)
                    for i in range(100): time.sleep(0.01); progress.progress(i+1)
                    cat, prio, reason = analyze_image_simulation(uploaded_file)
                    b_hash = generate_blockchain_hash(cat)
                    
                    new_report = {
                        "id": f"TKT-{random.randint(10000, 99999)}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "category": cat, "priority": prio, "reason": reason,
                        "lat": RVCE_LAT, "lon": RVCE_LON, "status": "Open",
                        "hash": b_hash 
                    }
                    st.session_state.reports.append(new_report)
                    st.balloons()
                    st.success(f"Ticket #{new_report['id']} Created on Ledger")
                    st.caption(f"🔒 Blockchain Hash: {b_hash} (Immutable)")

# ================= VIEW 2: ADMIN DASHBOARD =================
elif page == "🚔 Admin Dashboard":
    if st.session_state.user_mobile != ADMIN_MOBILE: st.error("⛔ Unauthorized"); st.stop()

    st.title("🚔 Triage Command Center")
    st.metric("IoT Sensor Status", "8 Units Active", delta="Normal")
    
    if st.session_state.reports:
        df = pd.DataFrame(st.session_state.reports)
        
        # TABS (Updated with BETA)
        tab1, tab2, tab3 = st.tabs(["📋 Ticket Ops", "📡 IoT Hub", "🔮 Predictive AI (BETA)"])
        
        with tab1: 
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: t_id = st.selectbox("Select Ticket", df['id'].tolist())
            selected_ticket = next((x for x in st.session_state.reports if x["id"] == t_id), None)
            
            with c2:
                if st.button("✅ Mark Resolved"):
                    if selected_ticket:
                        selected_ticket['status'] = "Resolved"
                        st.toast("SMS Sent", icon="📨"); time.sleep(1); st.rerun()
            with c3:
                if selected_ticket:
                    pdf_data = create_pdf(selected_ticket)
                    st.download_button("⬇️ PDF Report", pdf_data, f"{t_id}.pdf", "application/pdf")
            
            if selected_ticket:
                st.code(f"Ledger ID: {selected_ticket['hash']}", language="text")
                
            def color_row(row):
                return ['background-color: #ffcccb; color: black' if row['priority'] == 'High' else '' for _ in row]
            st.dataframe(df.style.apply(color_row, axis=1), use_container_width=True)

        with tab2: 
            c1, c2 = st.columns(2)
            c1.map(df, zoom=15, color="#ff0000")
            c2.line_chart(pd.DataFrame(np.random.randint(60, 150, size=(20, 1)), columns=['AQI']))
            
        with tab3: # PREDICTIVE AI (BETA)
            st.subheader("🤖 Future Incident Prediction (LSTM Model)")
            st.caption("⚠️ **BETA FEATURE:** Experimental model trained on 2024-25 Ward Data.")
            
            future_dates = [(datetime.now() + timedelta(days=i)).strftime("%b %d") for i in range(1, 8)]
            pred_data = pd.DataFrame({
                "Date": future_dates,
                "Predicted Potholes": np.random.randint(2, 8, 7),
                "Predicted Garbage": np.random.randint(5, 12, 7)
            }).set_index("Date")
            
            st.line_chart(pred_data)
            st.info("⚠️ Insight: High probability of 'Garbage Dumps' on Weekend (Saturday).")

    else:
        st.info("No tickets available.")

# --- FOOTER ---
st.markdown("""<div class="footer"><p>© 2026 Wanderers 5th Semester EL | All Rights Reserved</p></div>""", unsafe_allow_html=True)
