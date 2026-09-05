import streamlit as st
import pandas as pd
import joblib
import time
import os
import datetime
import random
from PIL import Image


# Page Config (custom icon used as favicon + sidebar logo)

ICON_PATH = "icon.png"
if os.path.exists(ICON_PATH):
    page_icon = Image.open(ICON_PATH)
else:
    page_icon = "❤️"

st.set_page_config(
    page_title="Heart Stroke & Health Care Platform",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)


# Splash Screen

if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash = st.empty()
    with splash.container():
        st.markdown("""
            <style>
            .splash-wrap {
                height: 80vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: radial-gradient(circle at center, #2b1055 0%, #0f0c29 100%);
                border-radius: 24px;
            }
            .splash-icon {
                width: 130px;
                height: 130px;
                animation: pulse 1.1s ease-in-out infinite;
                filter: drop-shadow(0 0 25px rgba(230,57,70,0.6));
            }
            @keyframes pulse {
                0%   { transform: scale(1); }
                50%  { transform: scale(1.12); }
                100% { transform: scale(1); }
            }
            .splash-title {
                color: white;
                font-size: 2.1rem;
                font-weight: 800;
                margin-top: 25px;
                letter-spacing: 0.5px;
            }
            .splash-sub {
                color: #cfcfe8;
                font-size: 1rem;
                margin-top: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

        if os.path.exists(ICON_PATH):
            import base64
            with open(ICON_PATH, "rb") as f:
                icon_b64 = base64.b64encode(f.read()).decode()
            icon_html = f'<img class="splash-icon" src="data:image/png;base64,{icon_b64}"/>'
        else:
            icon_html = '<div style="font-size:100px;">❤️</div>'

        st.markdown(f"""
            <div class="splash-wrap">
                {icon_html}
                <div class="splash-title">Heart Health & Prediction Platform</div>
                <div class="splash-sub">Loading your clinical dashboard, please wait...</div>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(2.0)
    st.session_state.splash_shown = True
    splash.empty()
    st.rerun()


# Custom CSS Styling

st.markdown("""
    <style>
    /* Overall background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #eef1f5 100%);
    }

    /* Title styling */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #e63946, #d90429);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.05rem;
        margin-top: 0px;
        margin-bottom: 25px;
    }

    /* Section headings */
    .section-heading {
        color: #1a1a2e;
        font-size: 1.4rem;
        font-weight: 800;
        margin: 10px 0 16px 0;
    }

    /* Hint box */
    .hint-box {
        background: #e7f1ff;
        color: #1a1a2e;
        border-left: 5px solid #4361ee;
        padding: 16px 20px;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 500;
    }
    .metric-card {
        background: #ffffff;
        padding: 18px 16px 16px 16px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.07);
        margin-bottom: 18px;
        text-align: center;
        border: 1px solid #eee;
        transition: 0.25s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 22px rgba(217,4,41,0.12);
    }
    .metric-icon {
        font-size: 1.6rem;
        margin-bottom: 4px;
    }
    .metric-label {
        color: #888;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #1a1a2e;
        font-size: 1.3rem;
        font-weight: 800;
    }

    /* Result box */
    .result-high {
        background: linear-gradient(135deg, #ff6b6b, #d90429);
        color: white;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(217,4,41,0.35);
    }
    .result-low {
        background: linear-gradient(135deg, #38b000, #008000);
        color: white;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(56,176,0,0.35);
    }

    /* Doctor Profile Cards */
    .doctor-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        transition: 0.2s;
    }
    .doctor-card:hover {
        border-color: #e63946;
        box-shadow: 0 6px 20px rgba(230,57,70,0.15);
    }
    .doctor-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 3px;
    }
    .doctor-spec {
        font-size: 0.95rem;
        font-weight: 600;
        color: #e63946;
        margin-bottom: 8px;
    }
    .doctor-detail {
        font-size: 0.88rem;
        color: #64748b;
        margin: 2px 0;
    }

    /* Booking Confirmation */
    .confirm-box {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 16px;
        padding: 24px;
        margin-top: 20px;
    }
    .confirm-title {
        color: #065f46;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 10px;
    }

    /* Sidebar header */
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #d90429;
        margin-bottom: 10px;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #d90429, #e63946);
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        padding: 12px 0px;
        border-radius: 12px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 18px rgba(217,4,41,0.4);
    }

    /* Chatbot Message Text Visibility & Dark Text Color */
    [data-testid="stChatMessage"],
    .stChatMessage {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 10px !important;
    }

    [data-testid="stChatMessage"] *,
    .stChatMessage *,
    [data-testid="stChatMessageContent"],
    [data-testid="stChatMessageContent"] *,
    .stChatMessage [data-testid="stMarkdownContainer"],
    .stChatMessage [data-testid="stMarkdownContainer"] * {
        color: #1E1E1E !important;
    }

    /* Ensure chat input text is also dark and readable */
    [data-testid="stChatInput"] textarea {
        color: #1E1E1E !important;
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)


# Load saved model, scaler, and expected columns

model = joblib.load("KNN_heart.pkl")
scaler = joblib.load("scaler.pkl")
expected_columns = joblib.load("columns.pkl")


# Header

st.markdown('<div class="main-title">❤️ Heart Health & Stroke Risk Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">by Safiya &nbsp;|&nbsp; AI-Powered Cardiac Risk Assessment, 24/7 Virtual Assistant & Specialist Care</div>', unsafe_allow_html=True)


# Sidebar Inputs

with st.sidebar:
    st.markdown('<div class="sidebar-title">🩺 Patient Clinical Details</div>', unsafe_allow_html=True)
    st.caption("Adjust patient parameters below and evaluate heart disease risk:")

    age = st.slider("Age (Years)", 18, 100, 40)
    sex = st.selectbox("Sex", ["M", "F"])
    chest_pain = st.selectbox("Chest Pain Type", ["ATA", "NAP", "TA", "ASY"],
                              help="ATA: Atypical Angina | NAP: Non-Anginal | TA: Typical Angina | ASY: Asymptomatic")
    resting_bp = st.number_input("Resting Blood Pressure (mm Hg)", 80, 200, 120)
    cholesterol = st.number_input("Serum Cholesterol (mg/dL)", 100, 600, 200)
    fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dL", [0, 1],
                              format_func=lambda x: "Yes (> 120 mg/dL)" if x == 1 else "No (≤ 120 mg/dL)")
    resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"],
                               help="Normal | ST: ST-T wave abnormality | LVH: Left ventricular hypertrophy")
    max_hr = st.slider("Max Heart Rate Achieved (bpm)", 60, 220, 150)
    exercise_angina = st.selectbox("Exercise-Induced Angina", ["Y", "N"],
                                  format_func=lambda x: "Yes" if x == "Y" else "No")
    oldpeak = st.slider("Oldpeak (ST Depression in mm)", 0.0, 6.0, 1.0)
    st_slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"],
                            help="Slope of peak exercise ST segment")

    predict_btn = st.button("🔍 Predict Risk", use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Quick Indicators Guide")
    st.caption("• **Resting BP**: Ideal < 120 mmHg\n• **Cholesterol**: Optimal < 200 mg/dL\n• **Fasting Sugar**: Normal < 100 mg/dL")


# Navigation Tabs

tab_predict, tab_chat, tab_doctor = st.tabs([
    "🩺 Heart Risk Predictor",
    "🤖 AI Health Assistant",
    "📅 Doctor Consultation Booking"
])


def metric_card(icon, label, value):
    """Return a fully self-contained HTML card."""
    return f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """


# ==========================================
# TAB 1: HEART RISK PREDICTOR
# ==========================================
with tab_predict:
    st.markdown('<div class="section-heading">📋 Entered Clinical Summary</div>', unsafe_allow_html=True)

    row1 = [
        ("🎂", "Age", f"{age} yrs"),
        ("💉", "Resting BP", f"{resting_bp} mmHg"),
        ("🩸", "Cholesterol", f"{cholesterol} mg/dL"),
        ("💓", "Max Heart Rate", f"{max_hr} bpm"),
    ]
    row2 = [
        ("🧍", "Sex", "Male" if sex == "M" else "Female"),
        ("💢", "Chest Pain", chest_pain),
        ("📈", "ST Slope", st_slope),
        ("🏃", "Exercise Angina", "Yes" if exercise_angina == "Y" else "No"),
    ]

    for row in (row1, row2):
        cols = st.columns(4)
        for col, (icon, label, value) in zip(cols, row):
            with col:
                st.markdown(metric_card(icon, label, value), unsafe_allow_html=True)

    st.markdown("---")

    if predict_btn:
        # Create raw input dictionary
        raw_input = {
            'Age': age,
            'RestingBP': resting_bp,
            'Cholesterol': cholesterol,
            'FastingBS': fasting_bs,
            'MaxHR': max_hr,
            'Oldpeak': oldpeak,
            'Sex_' + sex: 1,
            'ChestPainType_' + chest_pain: 1,
            'RestingECG_' + resting_ecg: 1,
            'ExerciseAngina_' + exercise_angina: 1,
            'ST_Slope_' + st_slope: 1
        }

        # Create input dataframe
        input_df = pd.DataFrame([raw_input])

        # Fill in missing columns with 0s
        for col in expected_columns:
            if col not in input_df.columns:
                input_df[col] = 0

        # Reorder columns
        input_df = input_df[expected_columns]

        # Scale the input
        scaled_input = scaler.transform(input_df)

        # Make prediction
        prediction = model.predict(scaled_input)[0]

        # Try to get probability
        proba = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(scaled_input)[0][1]

        st.markdown('<div class="section-heading">🎯 Clinical Prediction Result</div>', unsafe_allow_html=True)

        res_col1, res_col2 = st.columns([2, 1])

        with res_col1:
            if prediction == 1:
                st.markdown(
                    '<div class="result-high">⚠️ High Risk of Heart Disease Detected</div>',
                    unsafe_allow_html=True
                )
                st.warning(
                    "**Clinical Recommendation:** Your parameters indicate potential cardiovascular risks. "
                    "We strongly advise consulting a cardiologist for an ECG and comprehensive examination. "
                    "You can schedule an appointment directly using the **Doctor Consultation** tab."
                )
            else:
                st.markdown(
                    '<div class="result-low">✅ Low Risk of Heart Disease</div>',
                    unsafe_allow_html=True
                )
                st.success(
                    "**Great News!** Your entered parameters fall within lower cardiovascular risk percentiles. "
                    "Continue maintaining balanced nutrition, physical activity, and regular annual checkups."
                )

        with res_col2:
            if proba is not None:
                st.markdown(
                    metric_card("📊", "Risk Probability", f"{proba*100:.1f}%"),
                    unsafe_allow_html=True
                )
                st.progress(min(max(proba, 0.0), 1.0))
            else:
                st.info("Probability score not available for this model.")

        st.markdown("---")
        st.caption("⚕️ **Disclaimer:** This tool provides an estimate based on machine learning algorithms and does not constitute official medical diagnosis. Consult a licensed medical practitioner for clinical evaluation.")

    else:
        st.markdown(
            '<div class="hint-box">👈 Check the sidebar values and click <b>Predict Risk</b> to run the AI cardiac assessment.</div>',
            unsafe_allow_html=True
        )


# ==========================================
# TAB 2: AI HEALTH ASSISTANT CHATBOT
# ==========================================
with tab_chat:
    st.markdown('<div class="section-heading">🤖 CardioCare AI Health Assistant</div>', unsafe_allow_html=True)
    st.caption("Ask questions about heart health, diet recommendations, cholesterol, blood pressure, or lifestyle management.")

    # Rule & Knowledge-based Medical AI response engine
    def get_ai_response(prompt: str) -> str:
        p = prompt.lower()

        # Emergency keywords
        if any(w in p for w in ["emergency", "heart attack", "crushing", "severe pain", "radiating", "unconscious"]):
            return (
                "🚨 **EMERGENCY WARNING:** If you or someone around you is experiencing sudden crushing chest pressure, "
                "pain radiating to the left arm, neck, jaw, sudden shortness of breath, cold sweat, or extreme lightheadedness, "
                "**immediately call your local emergency services (911 or 112) or go to the nearest emergency room.** "
                "Do not attempt to drive yourself."
            )

        # Blood Pressure
        elif any(w in p for w in ["blood pressure", "bp", "hypertension", "systolic", "diastolic"]):
            return (
                "🩸 **Understanding Blood Pressure (BP):**\n\n"
                "- **Normal:** Less than 120/80 mm Hg\n"
                "- **Elevated:** 120-129 / < 80 mm Hg\n"
                "- **Stage 1 Hypertension:** 130-139 / 80-89 mm Hg\n"
                "- **Stage 2 Hypertension:** 140+ / 90+ mm Hg\n\n"
                "**Evidence-Based Ways to Lower BP Naturally:**\n"
                "1. **DASH Diet:** Focus on leafy vegetables, fruits, whole grains, and potassium-rich foods (bananas, spinach).\n"
                "2. **Sodium Reduction:** Limit sodium intake to under 1,500 - 2,000 mg per day.\n"
                "3. **Regular Aerobic Activity:** 30 minutes of brisk walking or swimming 5 days a week.\n"
                "4. **Stress Reduction:** Practice daily mindfulness or deep breathing exercises."
            )

        # Cholesterol
        elif any(w in p for w in ["cholesterol", "ldl", "hdl", "triglycerides", "lipid"]):
            return (
                "🧪 **Managing Cholesterol Levels:**\n\n"
                "- **Total Cholesterol:** Desirable under 200 mg/dL.\n"
                "- **LDL ('Bad' Cholesterol):** Optimal under 100 mg/dL (or <70 mg/dL if at high cardiovascular risk).\n"
                "- **HDL ('Good' Cholesterol):** 50+ mg/dL for women, 40+ mg/dL for men.\n"
                "- **Triglycerides:** Normal is below 150 mg/dL.\n\n"
                "**Actionable Lifestyle Tips:**\n"
                "- Increase soluble fiber (oats, barley, beans, apples).\n"
                "- Choose healthy unsaturated fats: Extra virgin olive oil, avocados, almonds, and walnuts.\n"
                "- Consume Omega-3 fatty acids (salmon, chia seeds, flaxseeds).\n"
                "- Minimize trans fats and processed meats."
            )

        # Diet / Nutrition
        elif any(w in p for w in ["diet", "food", "eat", "nutrition", "meal", "sugar"]):
            return (
                "🥗 **Cardio-Protective Nutrition (Mediterranean & DASH Plans):**\n\n"
                "- **Plentiful:** Green leafy vegetables, berries, legumes, whole grains, extra virgin olive oil.\n"
                "- **Moderate:** Lean poultry, fatty fish (rich in Omega-3), low-fat dairy, nuts and seeds.\n"
                "- **Avoid or Limit:** Added sugars, sodas, ultra-processed snacks, deep-fried foods, and high-sodium canned foods.\n"
                "- **Hydration:** Aim for 2-3 liters of water daily to maintain optimal blood volume and electrolyte balance."
            )

        # Exercise
        elif any(w in p for w in ["exercise", "workout", "gym", "running", "walking", "cardio", "fitness"]):
            return (
                "🏃 **Exercise Guidelines for Heart Health:**\n\n"
                "- **Recommendation (AHA):** At least 150 minutes of moderate-intensity aerobic exercise per week (e.g., 30 mins, 5 days/week), or 75 minutes of vigorous activity.\n"
                "- **Best Cardio Activities:** Brisk walking, cycling, swimming, rowing, low-impact aerobics.\n"
                "- **Strength Training:** Include light resistance training 2 times per week.\n"
                "- **Important Safety Caution:** If you experience dizziness, unusual chest tightness, or excessive breathlessness during exercise, stop immediately and consult a physician."
            )

        # Chest Pain types
        elif any(w in p for w in ["chest pain", "angina", "ata", "nap", "asy", "ta"]):
            return (
                "💢 **Clinical Chest Pain Classifications:**\n\n"
                "- **TA (Typical Angina):** Substernal chest pressure provoked by physical exertion or stress and relieved by rest or nitroglycerin.\n"
                "- **ATA (Atypical Angina):** Chest discomfort accompanied by unusual symptoms (fatigue, shortness of breath, nausea), often observed in women.\n"
                "- **NAP (Non-Anginal Pain):** Discomfort likely originating from musculoskeletal, gastrointestinal (acid reflux), or respiratory sources.\n"
                "- **ASY (Asymptomatic):** Absence of noticeable chest discomfort. Silent ischemia can still occur, especially in individuals with diabetes."
            )

        # Fasting Blood Sugar / Diabetes
        elif any(w in p for w in ["sugar", "diabetes", "fasting", "glucose"]):
            return (
                "🩸 **Blood Glucose & Heart Disease Connection:**\n\n"
                "- **Normal Fasting Glucose:** 70 to 99 mg/dL.\n"
                "- **Prediabetes:** 100 to 125 mg/dL.\n"
                "- **Diabetes:** 126 mg/dL or higher on repeat tests.\n\n"
                "Chronically high blood sugar damages blood vessels and the nerves controlling your heart, doubling the risk of coronary artery disease."
            )

        # Default fallback
        else:
            return (
                f"Heart health is influenced by interconnected factors: blood pressure, cholesterol, glucose control, "
                f"physical activity, and genetics.\n\n"
                f"**Key Pillars of Cardiovascular Wellness:**\n"
                f"1. **Monitor Numbers:** Keep Resting BP < 120/80 mmHg and Cholesterol < 200 mg/dL.\n"
                f"2. **Daily Movement:** At least 30 minutes of moderate cardio.\n"
                f"3. **Anti-inflammatory Diet:** Rich in antioxidants, fiber, and omega-3s.\n"
                f"4. **Restorative Sleep:** 7-8 hours per night to regulate cardiac stress hormones.\n\n"
                f"You can ask me specifically about **diet**, **exercise**, **cholesterol**, **blood pressure**, or **emergency warning signs**!"
            )

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I am **CardioCare AI**, your heart health assistant. "
                    "I can answer questions regarding cardiovascular prevention, blood pressure, "
                    "cholesterol management, exercise safety, and healthy nutrition. How can I help you today?"
                )
            }
        ]

    # Quick prompt buttons
    st.markdown("**Quick Topics:**")
    quick_cols = st.columns(4)
    quick_queries = [
        ("🥗 Heart-Healthy Diet", "What is the best diet for heart health?"),
        ("🩸 Lower Blood Pressure", "How can I lower my blood pressure naturally?"),
        ("🧪 Cholesterol Tips", "How to manage high cholesterol and LDL?"),
        ("🚨 Emergency Signs", "What are emergency warning signs of a heart attack?"),
    ]

    for col, (btn_label, query_text) in zip(quick_cols, quick_queries):
        with col:
            if st.button(btn_label, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": query_text})
                response = get_ai_response(query_text)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="❤️"):
                    st.markdown(msg["content"])

    # User input field
    user_query = st.chat_input("Type your heart health question here...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        ai_reply = get_ai_response(user_query)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
        st.rerun()

    if len(st.session_state.chat_history) > 1:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = [st.session_state.chat_history[0]]
            st.rerun()


# ==========================================
# TAB 3: DOCTOR CONSULTATION BOOKING
# ==========================================
with tab_doctor:
    st.markdown('<div class="section-heading">📅 Schedule a Cardiologist Consultation</div>', unsafe_allow_html=True)
    st.caption("Connect with top board-certified cardiologists for telehealth video visits or in-person examinations.")

    # Doctor Profiles Display
    doc_col1, doc_col2, doc_col3 = st.columns(3)

    with doc_col1:
        st.markdown("""
            <div class="doctor-card">
                <div class="doctor-name">👨‍⚕️ Dr. Rajesh Kumar, MD</div>
                <div class="doctor-spec">Senior Interventional Cardiologist</div>
                <div class="doctor-detail">🏥 Apollo Heart Institute</div>
                <div class="doctor-detail">⭐ 4.9/5 (340+ reviews) | 16 yrs exp</div>
                <div class="doctor-detail">💬 Angioplasty, Ischemia, Coronary Care</div>
            </div>
        """, unsafe_allow_html=True)

    with doc_col2:
        st.markdown("""
            <div class="doctor-card">
                <div class="doctor-name">👩‍⚕️ Dr. Sarah Jenkins, MD</div>
                <div class="doctor-spec">Preventive Cardiology & Lipidology</div>
                <div class="doctor-detail">🏥 Metro Heart & Vascular Center</div>
                <div class="doctor-detail">⭐ 4.95/5 (410+ reviews) | 13 yrs exp</div>
                <div class="doctor-detail">💬 Hypertension, Cholesterol, Women's Heart</div>
            </div>
        """, unsafe_allow_html=True)

    with doc_col3:
        st.markdown("""
            <div class="doctor-card">
                <div class="doctor-name">👨‍⚕️ Dr. Emily Chen, MD, FHRS</div>
                <div class="doctor-spec">Cardiac Electrophysiologist</div>
                <div class="doctor-detail">🏥 Stanford Cardiovascular Care</div>
                <div class="doctor-detail">⭐ 4.88/5 (290+ reviews) | 11 yrs exp</div>
                <div class="doctor-detail">💬 Arrhythmia, Palpitations, ECG Analysis</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📝 Patient Booking Details")

    if "booked_appointments" not in st.session_state:
        st.session_state.booked_appointments = []

    with st.form("doctor_booking_form"):
        f_col1, f_col2 = st.columns(2)

        with f_col1:
            pat_name = st.text_input("Patient Full Name *", placeholder="e.g. John Doe")
            pat_email = st.text_input("Email Address *", placeholder="e.g. john.doe@example.com")
            pat_phone = st.text_input("Phone Number *", placeholder="e.g. +1 555-019-2834")
            selected_doctor = st.selectbox(
                "Select Cardiologist *",
                [
                    "Dr. Rajesh Kumar, MD (Interventional Cardiology)",
                    "Dr. Sarah Jenkins, MD (Preventive Cardiology & Lipids)",
                    "Dr. Emily Chen, MD (Cardiac Electrophysiology & Arrhythmia)"
                ]
            )

        with f_col2:
            consult_mode = st.radio("Consultation Type *", ["💻 Virtual Telehealth (Video Call)", "🏥 In-Person Hospital Visit"])
            today = datetime.date.today()
            pref_date = st.date_input("Preferred Appointment Date *", min_value=today, value=today + datetime.timedelta(days=1))
            time_slot = st.selectbox(
                "Preferred Time Slot *",
                [
                    "09:00 AM - 10:00 AM",
                    "10:30 AM - 11:30 AM",
                    "01:30 PM - 02:30 PM",
                    "03:00 PM - 04:00 PM",
                    "05:00 PM - 06:00 PM"
                ]
            )
            urgency = st.selectbox("Urgency Level", ["Routine Checkup", "Recent High Risk Assessment", "Experiencing Discomfort"])

        symptoms_notes = st.text_area("Symptoms / Medical History Notes", placeholder="Briefly describe any chest discomfort, palpitations, family history, or medications...")
        share_summary = st.checkbox("Attach my latest risk assessment results from this session to the doctor's file.", value=True)

        submit_booking = st.form_submit_button("📅 Confirm & Book Appointment", use_container_width=True)

    if submit_booking:
        if not pat_name.strip():
            st.error("Please provide the patient's full name.")
        elif not pat_email.strip() and not pat_phone.strip():
            st.error("Please provide at least an email address or phone number for confirmation.")
        else:
            ref_id = f"CARDIO-{random.randint(1000, 9999)}"
            booking_record = {
                "ref_id": ref_id,
                "patient_name": pat_name,
                "email": pat_email,
                "phone": pat_phone,
                "doctor": selected_doctor,
                "mode": consult_mode,
                "date": str(pref_date),
                "time": time_slot,
                "urgency": urgency,
                "notes": symptoms_notes,
                "attached_assessment": share_summary,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.booked_appointments.append(booking_record)

            st.markdown(f"""
                <div class="confirm-box">
                    <div class="confirm-title">✅ Consultation Successfully Booked!</div>
                    <p><b>Booking Reference:</b> <code>{ref_id}</code></p>
                    <p><b>Patient:</b> {pat_name} &nbsp;|&nbsp; <b>Contact:</b> {pat_email or pat_phone}</p>
                    <p><b>Physician:</b> {selected_doctor}</p>
                    <p><b>Date & Time:</b> {pref_date.strftime('%B %d, %Y')} at {time_slot}</p>
                    <p><b>Mode:</b> {consult_mode}</p>
                    <p style="margin-top: 10px; font-size: 0.9rem; color: #065f46;">
                        ℹ️ A confirmation link with instructions and meeting details has been dispatched. 
                        Please have your recent blood test records or ECG tracings ready prior to the visit.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.balloons()

    # View Previous Bookings
    if st.session_state.booked_appointments:
        with st.expander("📋 View Confirmed Appointments in Current Session", expanded=False):
            for b in reversed(st.session_state.booked_appointments):
                st.markdown(f"**Ref: `{b['ref_id']}`** — {b['doctor']} on **{b['date']}** at **{b['time']}** ({b['mode']}) for *{b['patient_name']}*")