import streamlit as st
import pandas as pd
import os
import subprocess
import csv
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# =========================
# PATHS CONFIGURATION
# =========================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "DSA part")
ML_DIR = os.path.join(BASE_DIR, "ml")

PYTHON_EXE = os.path.join(BASE_DIR, "semester_project", "Scripts", "python.exe")
PREDICT_SCRIPT = os.path.join(ML_DIR, "predict.py")

SYMPTOMS_FILE = os.path.join(BASE_DIR, "symptoms.txt")
AI_INPUT_FILE = os.path.join(BASE_DIR, "ai_input.csv")

FILES = {
    "patients": os.path.join(DATA_DIR, "patients.csv"),
    "doctors": os.path.join(DATA_DIR, "doctors.csv"),
    "staff": os.path.join(DATA_DIR, "staff.csv"),
    "appointments": os.path.join(DATA_DIR, "appointments.csv"),
    "emergencies": os.path.join(DATA_DIR, "emergency_cases.csv"),
    "bills": os.path.join(DATA_DIR, "bills.csv")
}

os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# PAGE CONFIGURATION
# =========================
st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS STYLING
# =========================
st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
        padding: 2rem 1rem;
    }
    
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .css-1d391kg {
        padding: 1rem;
    }
    
    /* Button styling */
    div.stButton > button {
        width: 100%;
        height: 50px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #e0e7ff;
        border-radius: 8px;
        font-weight: 600;
        color: #1e40af;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    
    .stError {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }
    
    /* Headers */
    h1 {
        color: #1e40af;
        font-weight: 800;
        margin-bottom: 2rem;
    }
    
    h2, h3 {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            
    }
</style>
""", unsafe_allow_html=True)

# =========================
# UTILITY FUNCTIONS
# =========================
def extract_confidence(result_text):
    for line in result_text.splitlines():
        if "Confidence" in line:
            try:
                return float(line.split(":")[1].replace("%", "").strip())
            except:
                return None
    return None


def load_csv(name, cols):
    """Load CSV file or create empty DataFrame"""
    path = FILES[name]
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_csv(df, name):
    """Save DataFrame to CSV"""
    os.makedirs(os.path.dirname(FILES[name]), exist_ok=True)
    df.to_csv(FILES[name], index=False)

def load_symptoms():
    """Load symptoms from file"""
    if os.path.exists(SYMPTOMS_FILE):
        with open(SYMPTOMS_FILE) as f:
            return [x.strip() for x in f if x.strip()]
    return []

CATEGORY_TO_DOCTOR = {
    "Heart": "Cardiologist",
    "Brain": "Neurologist",
    "Respiratory": "Pulmonologist",
    "Liver": "Hepatologist",
    "Endocrine": "Endocrinologist",
    "Skin": "Dermatologist",
    "General": "General Physician"
}


SYMPTOM_ALIASES = {

    # =====================
    # HEART
    # =====================
    "chest pain": "chest_pain",
    "pressure in chest": "chest_pain",
    "heart pain": "chest_pain",
    "short breath": "breathlessness",
    "shortness of breath": "breathlessness",
    "difficulty breathing": "breathlessness",
    "fast heart rate": "fast_heart_rate",
    "rapid heartbeat": "fast_heart_rate",
    "palpitations": "palpitations",
    "sweating": "sweating",

    # =====================
    # RESPIRATORY
    # =====================
    "breathing problem": "breathlessness",
    "breathing difficulty": "breathlessness",
    "chest congestion": "congestion",
    "cough": "cough",
    "phlegm": "phlegm",
    "mucus": "mucoid_sputum",
    "runny nose": "runny_nose",
    "sinus pressure": "sinus_pressure",
    "wheezing": "phlegm",

    # =====================
    # BRAIN / NEURO
    # =====================
    "severe headache": "headache",
    "headache": "headache",
    "dizziness": "dizziness",
    "confusion": "altered_sensorium",
    "memory loss": "lack_of_concentration",
    "blurred vision": "blurred_and_distorted_vision",
    "loss of balance": "loss_of_balance",
    "slurred speech": "slurred_speech",
    "seizure": "coma",

    # =====================
    # LIVER
    # =====================
    "yellow skin": "yellowish_skin",
    "yellow eyes": "yellowing_of_eyes",
    "dark urine": "dark_urine",
    "abdominal pain": "abdominal_pain",
    "loss of appetite": "loss_of_appetite",
    "alcohol history": "history_of_alcohol_consumption",

    # =====================
    # ENDOCRINE
    # =====================
    "weight gain": "weight_gain",
    "weight loss": "weight_loss",
    "fatigue": "fatigue",
    "excessive hunger": "excessive_hunger",
    "frequent urination": "polyuria",
    "increased appetite": "increased_appetite",

    # =====================
    # MENTAL HEALTH
    # =====================
    "anxiety": "anxiety",
    "panic": "anxiety",
    "depression": "depression",
    "mood swings": "mood_swings",
    "irritability": "irritability",
    "insomnia": "restlessness"
}


def create_ai_input(user_text):
    """Create AI input file with smart symptom matching"""
    all_symptoms = load_symptoms()
    if not all_symptoms:
        return False

    user_text = user_text.lower()
    detected = set()

    # 1️⃣ Phrase-based smart matching
    for phrase, canonical in SYMPTOM_ALIASES.items():
        if phrase in user_text:
            detected.add(canonical)

    # 2️⃣ Exact fallback match (underscore-safe)
    for s in all_symptoms:
        if s.replace("_", " ") in user_text:
            detected.add(s)

    # 3️⃣ Write AI input
    with open(AI_INPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(all_symptoms + ["prognosis"])
        row = [1 if s in detected else 0 for s in all_symptoms]
        row.append("?")
        writer.writerow(row)

    return True

def rule_based_override(symptoms_text):
    text = symptoms_text.lower()

    # Heart-related red flags
    heart_triggers = [
        "chest pain",
        "short breath",
        "shortness of breath",
        "difficulty breathing",
        "sweating",
        "palpitations",
        "fast heart rate"
    ]

    heart_score = sum(1 for t in heart_triggers if t in text)

    if heart_score >= 2:
        return {
            "Category": "Heart",
            "Doctor": "Cardiologist",
            "Confidence": "High (Rule-based Safety Override)"
        }

    # Respiratory-related red flags
    respiratory_triggers = [
        "breathing problem",
        "breathing difficulty",
        "shortness of breath",
        "cough",
        "phlegm",
        "chest congestion",
        "wheezing"
    ]

    resp_score = sum(1 for t in respiratory_triggers if t in text)

    if resp_score >= 2:
        return {
            "Category": "Respiratory",
            "Doctor": "Pulmonologist",
            "Confidence": "High (Rule-based Safety Override)"
        }

    return None


def run_ai_prediction():
    """Run AI prediction script"""
    try:
        result = subprocess.run(
            [PYTHON_EXE, PREDICT_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        return f"Error running prediction: {str(e)}"

def get_next_id(df, id_col="ID"):
    """Get next available ID"""
    if len(df) == 0:
        return 1
    return int(df[id_col].max()) + 1

# =========================
# SESSION STATE INITIALIZATION
# =========================
if "billing_stack" not in st.session_state:
    st.session_state.billing_stack = []

if "current_patient_id" not in st.session_state:
    st.session_state.current_patient_id = None

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None


# =========================
# SIDEBAR NAVIGATION
# =========================
st.sidebar.title("🏥 Hospital System")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📋 Navigation",
    [
        "🏠 Dashboard",
        "👤 Patient Management",
        "🩺 Doctor Management", 
        "👨‍⚕️ Staff Management",
        "💳 Billing System",
        "📅 Appointment Scheduling",
        "🚨 Emergency Cases",
        "📊 Analytics & Reports"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("**Smart Hospital Management System**\n\nIntegrated DSA + AI System")

# =========================
# 1. DASHBOARD
# =========================
if menu == "🏠 Dashboard":
    st.title("🏠 Hospital Management Dashboard")
    st.markdown("### Real-time System Overview")
    
    # Load all data
    patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
    doctors_df = load_csv("doctors", ["ID","Name","Specialization","Experience","Contact","Availability"])
    staff_df = load_csv("staff", ["ID","Name","Shift","Department"])
    appointments_df = load_csv("appointments", ["PatientID","DoctorID","Date","Time","Type","Severity"])
    emergencies_df = load_csv("emergencies", ["PatientID","Symptoms","Severity","Time"])
    
    # Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="👥 Total Patients",
            value=len(patients_df),
            delta=f"+{len(patients_df[patients_df.index >= len(patients_df)-5])}" if len(patients_df) > 0 else "0"
        )
    
    with col2:
        st.metric(
            label="🩺 Active Doctors",
            value=len(doctors_df),
            delta=f"{len(doctors_df[doctors_df['Availability'] == 'Available']) if 'Availability' in doctors_df.columns else 0} Available"
        )
    
    with col3:
        st.metric(
            label="👨‍⚕️ Staff Members",
            value=len(staff_df),
            delta=f"{len(staff_df[staff_df['Shift'] == 'Morning']) if 'Shift' in staff_df.columns else 0} Morning"
        )
    
    with col4:
        st.metric(
            label="📅 Appointments",
            value=len(appointments_df),
            delta=f"{len(appointments_df[appointments_df['Type'] == 'Emergency']) if 'Type' in appointments_df.columns else 0} Emergency"
        )
    
    with col5:
        st.metric(
            label="🚨 Emergency Cases",
            value=len(emergencies_df),
            delta=f"{len(emergencies_df[emergencies_df['Severity'] >= 7]) if 'Severity' in emergencies_df.columns else 0} Critical"
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Patient Demographics")
        if len(patients_df) > 0 and 'Gender' in patients_df.columns:
            gender_counts = patients_df['Gender'].value_counts()
            fig = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Gender Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No patient data available")
    
    with col2:
        st.subheader("🚨 Emergency Severity Levels")
        if len(emergencies_df) > 0 and 'Severity' in emergencies_df.columns:
            severity_counts = emergencies_df['Severity'].value_counts().sort_index()
            fig = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                labels={'x': 'Severity Level', 'y': 'Count'},
                title="Emergency Cases by Severity",
                color=severity_counts.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No emergency data available")
    
    # Recent Activity
    st.markdown("---")
    st.subheader("📋 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Recent Patients**")
        if len(patients_df) > 0:
            recent_patients = patients_df.tail(5)[['ID', 'Name', 'Age']]
            st.dataframe(recent_patients, use_container_width=True, hide_index=True)
        else:
            st.info("No recent patients")
    
    with col2:
        st.markdown("**Upcoming Appointments**")
        if len(appointments_df) > 0:
            recent_appointments = appointments_df.head(5)[['PatientID', 'DoctorID', 'Date', 'Type']]
            st.dataframe(recent_appointments, use_container_width=True, hide_index=True)
        else:
            st.info("No upcoming appointments")

# =========================
# 2. PATIENT MANAGEMENT
# =========================
elif menu == "👤 Patient Management":
    st.title("👤 Patient Management System")
    st.markdown("### Manage patient records with linked list data structure")
    
    df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Register Patient",
        "🔍 Search Patient",
        "✏️ Update Patient",
        "🗑️ Delete Patient",
        "📋 All Patients"
    ])
    
    # Register New Patient
    with tab1:
        st.subheader("Register New Patient")
        
        with st.form("add_patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", placeholder="Enter patient name")
                age = st.number_input("Age*", min_value=0, max_value=150, value=25)
                gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            
            with col2:
                contact = st.text_input("Contact Number*", placeholder="+92-XXX-XXXXXXX")
                medical_history = st.text_area("Medical History", placeholder="Previous conditions, allergies, etc.")
            
            symptoms = st.text_input("Current Symptoms*", placeholder="fever cough headache")
            
            use_ai = st.checkbox("🤖 Use AI for Disease Prediction", value=True)
            
            submitted = st.form_submit_button("Register Patient", use_container_width=True)
            
            if submitted:
                st.session_state.ai_result = None
                if name and age and gender and contact and symptoms:
                    new_id = get_next_id(df)
                    new_patient = pd.DataFrame([{
                        "ID": new_id,
                        "Name": name,
                        "Age": age,
                        "Gender": gender,
                        "Contact": contact,
                        "MedicalHistory": medical_history,
                        "Symptoms": symptoms
                    }])
                    
                    df = pd.concat([df, new_patient], ignore_index=True)
                    save_csv(df, "patients")
                    
                    st.success(f"✅ Patient registered successfully! Assigned ID: {new_id}")
                    
                    if use_ai:
                        with st.spinner("🤖 Running AI prediction..."):
                            override = rule_based_override(symptoms)

                            if override:
                                st.session_state.ai_result = (
                                    "AI MEDICAL ASSISTANT RESULT\n"
                                    "----------------------------\n"
                                    "Disease Identified : Possible Heart Condition\n"
                                    f"Category           : {override['Category']}\n"
                                    f"Confidence          : {override['Confidence']}\n"
                                    f"Recommended Doctor  : {override['Doctor']}\n"
                                    "----------------------------"
                                )
                            else:
                                if create_ai_input(symptoms):
                                    st.session_state.ai_result = run_ai_prediction()
                                    conf = extract_confidence(st.session_state.ai_result)
                                    if conf is not None and conf < 55:
                                        st.session_state.ai_result += (
                                            "\n⚠️ NOTE: Low confidence prediction.\n"
                                            "Patient should be reviewed by a General Physician first."
                                        )

                                else:
                                    st.session_state.ai_result = "AI prediction unavailable - symptoms file not found"

                else:
                    st.error("❌ Please fill all required fields marked with *")
            # 🔽 SHOW AI RESULT AFTER FORM SUBMISSION
        st.subheader("🤖 AI Disease Prediction Result")
        if st.session_state.ai_result is not None:
            st.code(st.session_state.ai_result)
        else:
            st.warning("AI did not return any output.")

    
    # Search Patient
    with tab2:
        st.subheader("Search Patient by ID")
        
        search_id = st.number_input("Enter Patient ID", min_value=1, value=1, key="search_id")
        
        if st.button("🔍 Search", use_container_width=True):
            patient = df[df['ID'] == search_id]
            
            if len(patient) > 0:
                st.success("✅ Patient Found!")
                
                patient_data = patient.iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**ID:** {patient_data['ID']}")
                    st.markdown(f"**Name:** {patient_data['Name']}")
                    st.markdown(f"**Age:** {patient_data['Age']}")
                    st.markdown(f"**Gender:** {patient_data['Gender']}")
                
                with col2:
                    st.markdown(f"**Contact:** {patient_data['Contact']}")
                    st.markdown(f"**Medical History:** {patient_data['MedicalHistory']}")
                    st.markdown(f"**Symptoms:** {patient_data['Symptoms']}")
            else:
                st.error("❌ Patient not found!")
    
    # Update Patient
    with tab3:
        st.subheader("Update Patient Information")
        
        update_id = st.number_input("Enter Patient ID to Update", min_value=1, value=1, key="update_id")
        
        patient = df[df['ID'] == update_id]
        
        if len(patient) > 0:
            patient_data = patient.iloc[0]
            
            with st.form("update_patient_form"):
                st.info(f"Updating Patient: **{patient_data['Name']}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("New Name", value=patient_data['Name'])
                    new_age = st.number_input("New Age", value=int(patient_data['Age']), min_value=0, max_value=150)
                
                with col2:
                    new_contact = st.text_input("New Contact", value=patient_data['Contact'])
                    new_history = st.text_area("Medical History", value=patient_data['MedicalHistory'])
                
                new_symptoms = st.text_input("Current Symptoms", value=patient_data['Symptoms'])
                
                update_submitted = st.form_submit_button("Update Patient", use_container_width=True)
                
                if update_submitted:
                    df.loc[df['ID'] == update_id, 'Name'] = new_name
                    df.loc[df['ID'] == update_id, 'Age'] = new_age
                    df.loc[df['ID'] == update_id, 'Contact'] = new_contact
                    df.loc[df['ID'] == update_id, 'MedicalHistory'] = new_history
                    df.loc[df['ID'] == update_id, 'Symptoms'] = new_symptoms
                    
                    save_csv(df, "patients")
                    st.success("✅ Patient information updated successfully!")
                    st.rerun()
        else:
            st.warning("⚠️ Enter a valid Patient ID to update")
    
    # Delete Patient
    with tab4:
        st.subheader("Remove Patient Record")
        
        delete_id = st.number_input("Enter Patient ID to Delete", min_value=1, value=1, key="delete_id")
        
        patient = df[df['ID'] == delete_id]
        
        if len(patient) > 0:
            patient_data = patient.iloc[0]
            st.warning(f"⚠️ You are about to delete: **{patient_data['Name']}** (ID: {delete_id})")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirm Delete", use_container_width=True, type="primary"):
                    df = df[df['ID'] != delete_id]
                    save_csv(df, "patients")
                    st.success("✅ Patient removed successfully!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.info("Delete operation cancelled")
        else:
            st.info("Enter a valid Patient ID to delete")
    
    # Display All Patients
    # Display All Patients
    with tab5:
        st.subheader("All Patient Records")

        if len(df) > 0:
            numeric_cols = df.select_dtypes(include="number").columns

            if len(numeric_cols) > 0:
                st.dataframe(
                    df.style.highlight_max(subset=numeric_cols, color="lightgreen"),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            st.download_button(
                label="📥 Download Patient Records (CSV)",
                data=df.to_csv(index=False),
                file_name=f"patients_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📋 No patients registered yet")


# =========================
# 3. DOCTOR MANAGEMENT
# =========================
elif menu == "🩺 Doctor Management":
    st.title("🩺 Doctor Management System")
    st.markdown("### Manage doctor records with linked list data structure")
    
    df = load_csv("doctors", ["ID","Name","Specialization","Experience","Contact","Availability"])
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add Doctor",
        "🔍 Search by Specialization",
        "📋 All Doctors",
        "✏️ Update Doctor"
    ])
    
    # Add New Doctor
    with tab1:
        st.subheader("Register New Doctor")
        
        with st.form("add_doctor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", placeholder="Dr. John Doe")
                specialization = st.selectbox(
                    "Specialization*",
                    ["Cardiologist", "Neurologist", "Pulmonologist", "Hepatologist",
                     "Endocrinologist", "Psychiatrist", "Dermatologist", "General Physician",
                     "Pediatrician", "Orthopedic", "ENT Specialist"]
                )
                experience = st.number_input("Years of Experience*", min_value=0, max_value=50, value=5)
            
            with col2:
                contact = st.text_input("Contact Number*", placeholder="+92-XXX-XXXXXXX")
                availability = st.text_input("Available Time Slots*", placeholder="9AM-5PM, Mon-Fri")
            
            submitted = st.form_submit_button("Add Doctor", use_container_width=True)
            
            if submitted:
                if name and specialization and contact and availability:
                    new_id = get_next_id(df)
                    new_doctor = pd.DataFrame([{
                        "ID": new_id,
                        "Name": name,
                        "Specialization": specialization,
                        "Experience": experience,
                        "Contact": contact,
                        "Availability": availability
                    }])
                    
                    df = pd.concat([df, new_doctor], ignore_index=True)
                    save_csv(df, "doctors")
                    
                    st.success(f"✅ Doctor registered successfully! Assigned ID: {new_id}")
                else:
                    st.error("❌ Please fill all required fields")
    
    # Search by Specialization
    with tab2:
        st.subheader("Search Doctors by Specialization")
        
        search_spec = st.selectbox(
            "Select Specialization",
            ["All"] + list(df['Specialization'].unique()) if len(df) > 0 else ["All"]
        )
        
        if search_spec != "All" and len(df) > 0:
            filtered = df[df['Specialization'] == search_spec]
            
            if len(filtered) > 0:
                st.success(f"✅ Found {len(filtered)} doctor(s) in {search_spec}")
                st.dataframe(filtered, use_container_width=True, hide_index=True)
            else:
                st.warning(f"⚠️ No doctors found with specialization: {search_spec}")
        elif len(df) > 0:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📋 No doctors registered yet")
    
    # All Doctors
    with tab3:
        st.subheader("All Registered Doctors")
        
        if len(df) > 0:
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Doctors", len(df))
            with col2:
                most_common = df['Specialization'].mode()[0] if len(df) > 0 else "N/A"
                st.metric("Most Common Specialty", most_common)
            with col3:
                avg_exp = df['Experience'].mean() if len(df) > 0 else 0
                st.metric("Avg Experience", f"{avg_exp:.1f} years")
            
            st.markdown("---")
            
            st.dataframe(
                df.style.highlight_max(axis=0, subset=['Experience'], color='lightgreen'),
                use_container_width=True,
                hide_index=True
            )
            
            st.download_button(
                label="📥 Download Doctor Records (CSV)",
                data=df.to_csv(index=False),
                file_name=f"doctors_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📋 No doctors registered yet")
    
    # Update Doctor
    with tab4:
        st.subheader("Update Doctor Information")
        
        if len(df) > 0:
            update_id = st.selectbox("Select Doctor to Update", df['ID'].tolist())
            
            doctor = df[df['ID'] == update_id].iloc[0]
            
            with st.form("update_doctor_form"):
                st.info(f"Updating: **{doctor['Name']}**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_contact = st.text_input("Contact", value=doctor['Contact'])
                    new_availability = st.text_input("Availability", value=doctor['Availability'])
                
                with col2:
                    new_experience = st.number_input("Experience", value=int(doctor['Experience']), min_value=0)
                
                if st.form_submit_button("Update Doctor", use_container_width=True):
                    df.loc[df['ID'] == update_id, 'Contact'] = new_contact
                    df.loc[df['ID'] == update_id, 'Availability'] = new_availability
                    df.loc[df['ID'] == update_id, 'Experience'] = new_experience
                    
                    save_csv(df, "doctors")
                    st.success("✅ Doctor information updated!")
                    st.rerun()
        else:
            st.info("No doctors available to update")

# =========================
# 4. STAFF MANAGEMENT
# =========================
elif menu == "👨‍⚕️ Staff Management":
    st.title("👨‍⚕️ Staff Management System")
    st.markdown("### Manage staff with linked list and duty queue")
    
    df = load_csv("staff", ["ID","Name","Shift","Department"])
    
    tab1, tab2, tab3 = st.tabs([
        "➕ Add Staff",
        "👷 Duty Roster (Queue)",
        "📋 All Staff"
    ])
    
    # Add Staff
    with tab1:
        st.subheader("Register New Staff Member")
        
        with st.form("add_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", placeholder="Enter staff name")
                shift = st.selectbox("Shift*", ["Morning", "Evening", "Night"])
            
            with col2:
                department = st.selectbox(
                    "Department*",
                    ["Emergency", "ICU", "OPD", "Laboratory", "Pharmacy",
                     "Radiology", "Administration", "Housekeeping"]
                )
            
            submitted = st.form_submit_button("Add Staff Member", use_container_width=True)
            
            if submitted:
                if name and shift and department:
                    new_id = get_next_id(df)
                    new_staff = pd.DataFrame([{
                        "ID": new_id,
                        "Name": name,
                        "Shift": shift,
                        "Department": department
                    }])
                    
                    df = pd.concat([df, new_staff], ignore_index=True)
                    save_csv(df, "staff")
                    
                    st.success(f"✅ Staff member registered! ID: {new_id}")
                else:
                    st.error("❌ Please fill all required fields")
    
    # Duty Roster
    with tab2:
        st.subheader("🔄 Duty Rotation Queue (FIFO)")
        st.markdown("*First-In-First-Out duty assignment system*")
        
        if len(df) > 0:
            # Show duty queue in order
            st.info(f"📋 **{len(df)} staff members** in rotation queue")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Current Duty Order:**")
                for idx, staff in df.iterrows():
                    st.markdown(
                        f"{idx + 1}. **{staff['Name']}** - {staff['Department']} "
                        f"({staff['Shift']} Shift)"
                    )
            
            with col2:
                st.markdown("**Queue Operations:**")
                
                if st.button("🎯 Assign Next Duty", use_container_width=True):
                    next_staff = df.iloc[0]
                    st.success(
                        f"✅ **{next_staff['Name']}** assigned to duty!\n\n"
                        f"Department: {next_staff['Department']}\n\n"
                        f"Shift: {next_staff['Shift']}"
                    )
                    
                    # Move to end of queue
                    df = pd.concat([df.iloc[1:], df.iloc[:1]], ignore_index=True)
                    save_csv(df, "staff")
                
                if st.button("🔄 Rotate Queue", use_container_width=True):
                    if len(df) > 1:
                        df = pd.concat([df.iloc[1:], df.iloc[:1]], ignore_index=True)
                        save_csv(df, "staff")
                        st.success("✅ Queue rotated!")
                        st.rerun()
        else:
            st.info("📋 No staff members in duty roster")
    
    # All Staff
    with tab3:
        st.subheader("All Staff Members")
        
        if len(df) > 0:
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Staff", len(df))
            with col2:
                shift_counts = df['Shift'].value_counts()
                most_shift = shift_counts.index[0] if len(shift_counts) > 0 else "N/A"
                st.metric("Most Common Shift", most_shift)
            with col3:
                dept_counts = df['Department'].value_counts()
                most_dept = dept_counts.index[0] if len(dept_counts) > 0 else "N/A"
                st.metric("Largest Department", most_dept)
            
            st.markdown("---")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                filter_shift = st.multiselect("Filter by Shift", df['Shift'].unique())
            with col2:
                filter_dept = st.multiselect("Filter by Department", df['Department'].unique())
            
            filtered_df = df.copy()
            if filter_shift:
                filtered_df = filtered_df[filtered_df['Shift'].isin(filter_shift)]
            if filter_dept:
                filtered_df = filtered_df[filtered_df['Department'].isin(filter_dept)]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.info("📋 No staff members registered yet")

# =========================
# 5. BILLING SYSTEM
# =========================
elif menu == "💳 Billing System":
    st.title("💳 Hospital Billing System")
    st.markdown("### Stack-based billing with undo functionality")
    
    tab1, tab2, tab3 = st.tabs([
        "🧾 Create Bill",
        "📋 Billing History",
        "💰 Financial Summary"
    ])
    
    # Create Bill
    with tab1:
        st.subheader("Generate Patient Bill")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Add Billing Items (Stack Operations)**")
            
            with st.form("add_item_form"):
                item_type = st.radio("Item Type", ["💊 Medicine", "🏥 Service", "🛏️ Room Charge"])
                item_desc = st.text_input("Description*", placeholder="Item name/description")
                item_cost = st.number_input("Amount ($)*", min_value=0.0, step=0.01, format="%.2f")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    add_item = st.form_submit_button("➕ Add to Bill (Push)", use_container_width=True)
                with col_b:
                    if st.form_submit_button("↩️ Undo Last (Pop)", use_container_width=True):
                        if st.session_state.billing_stack:
                            removed = st.session_state.billing_stack.pop()
                            st.success(f"✅ Removed: {removed[0]} (${removed[1]:.2f})")
                            st.rerun()
                        else:
                            st.warning("⚠️ No items to remove!")
                
                if add_item and item_desc and item_cost > 0:
                    st.session_state.billing_stack.append((item_desc, item_cost, item_type))
                    st.success(f"✅ Added to bill: {item_desc}")
                    st.rerun()
        
        with col2:
            st.markdown("**Current Bill Stack**")
            
            if st.session_state.billing_stack:
                total = 0
                st.markdown("---")
                for idx, (desc, cost, itype) in enumerate(reversed(st.session_state.billing_stack)):
                    st.markdown(f"**{len(st.session_state.billing_stack) - idx}.** {itype} {desc}")
                    st.markdown(f"   💰 ${cost:.2f}")
                    total += cost
                
                st.markdown("---")
                st.markdown(f"### **Total: ${total:.2f}**")
                
                if st.button("🧾 Generate Final Bill", use_container_width=True, type="primary"):
                    # Save bill
                    bills_df = load_csv("bills", ["BillID", "Date", "Items", "Total"])
                    
                    bill_id = get_next_id(bills_df, "BillID")
                    bill_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    items_str = " | ".join([f"{d}: ${c:.2f}" for d, c, _ in st.session_state.billing_stack])
                    
                    new_bill = pd.DataFrame([{
                        "BillID": bill_id,
                        "Date": bill_date,
                        "Items": items_str,
                        "Total": total
                    }])
                    
                    bills_df = pd.concat([bills_df, new_bill], ignore_index=True)
                    save_csv(bills_df, "bills")
                    
                    st.success(f"✅ Bill #{bill_id} generated successfully!")
                    
                    # Show receipt
                    st.markdown("---")
                    st.markdown("### 🧾 RECEIPT")
                    st.markdown(f"**Bill ID:** {bill_id}")
                    st.markdown(f"**Date:** {bill_date}")
                    st.markdown("**Items:**")
                    for desc, cost, itype in st.session_state.billing_stack:
                        st.markdown(f"- {desc}: ${cost:.2f}")
                    st.markdown(f"### **TOTAL: ${total:.2f}**")
                    
                    # Clear stack
                    st.session_state.billing_stack = []
                
                if st.button("🗑️ Clear All Items", use_container_width=True):
                    st.session_state.billing_stack = []
                    st.success("✅ Bill cleared!")
                    st.rerun()
            else:
                st.info("📝 Bill stack is empty\n\nAdd items to start billing")
    
    # Billing History
    with tab2:
        st.subheader("Billing Records")
        
        bills_df = load_csv("bills", ["BillID", "Date", "Items", "Total"])
        
        if len(bills_df) > 0:
            st.dataframe(bills_df, use_container_width=True, hide_index=True)
            
            st.download_button(
                label="📥 Download Billing History (CSV)",
                data=bills_df.to_csv(index=False),
                file_name=f"bills_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📋 No billing records found")
    
    # Financial Summary
    with tab3:
        st.subheader("Financial Analytics")
        
        bills_df = load_csv("bills", ["BillID", "Date", "Items", "Total"])
        
        if len(bills_df) > 0 and 'Total' in bills_df.columns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Bills", len(bills_df))
            with col2:
                total_revenue = bills_df['Total'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col3:
                avg_bill = bills_df['Total'].mean()
                st.metric("Average Bill", f"${avg_bill:,.2f}")
            
            st.markdown("---")
            
            # Revenue chart
            if 'Date' in bills_df.columns:
                bills_df['Date'] = pd.to_datetime(bills_df['Date'])
                bills_df['DateOnly'] = bills_df['Date'].dt.date
                
                daily_revenue = bills_df.groupby('DateOnly')['Total'].sum().reset_index()
                
                fig = px.line(
                    daily_revenue,
                    x='DateOnly',
                    y='Total',
                    title='Daily Revenue Trend',
                    labels={'DateOnly': 'Date', 'Total': 'Revenue ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No billing data available for analysis")

# =========================
# 6. APPOINTMENT SCHEDULING
# =========================
elif menu == "📅 Appointment Scheduling":
    st.title("📅 Appointment Scheduling System")
    st.markdown("### Queue + Max Heap for priority-based scheduling")
    
    df = load_csv("appointments", ["PatientID","DoctorID","Date","Time","Type","Severity"])
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Book Regular Appointment",
        "🚨 Book Emergency Appointment",
        "▶️ Process Next Appointment",
        "📊 Appointment Overview"
    ])
    
    # Book Regular Appointment
    with tab1:
        st.subheader("Schedule Regular Appointment (Queue - FIFO)")
        
        patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
        doctors_df = load_csv("doctors", ["ID","Name","Specialization","Experience","Contact","Availability"])
        
        with st.form("regular_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                if len(patients_df) > 0:
                    patient_options = [f"{row['ID']} - {row['Name']}" for _, row in patients_df.iterrows()]
                    selected_patient = st.selectbox("Select Patient*", patient_options)
                    patient_id = int(selected_patient.split(" - ")[0])
                else:
                    st.warning("No patients registered")
                    patient_id = st.number_input("Patient ID*", min_value=1)
                
                appointment_date = st.date_input("Appointment Date*")
            
            with col2:
                if len(doctors_df) > 0:
                    doctor_options = [f"{row['ID']} - {row['Name']} ({row['Specialization']})" 
                                    for _, row in doctors_df.iterrows()]
                    selected_doctor = st.selectbox("Select Doctor*", doctor_options)
                    doctor_id = int(selected_doctor.split(" - ")[0])
                else:
                    st.warning("No doctors registered")
                    doctor_id = st.number_input("Doctor ID*", min_value=1)
                
                appointment_time = st.time_input("Appointment Time*")
            
            submitted = st.form_submit_button("📅 Schedule Regular Appointment", use_container_width=True)
            
            if submitted:
                new_appointment = pd.DataFrame([{
                    "PatientID": patient_id,
                    "DoctorID": doctor_id,
                    "Date": str(appointment_date),
                    "Time": str(appointment_time),
                    "Type": "Regular",
                    "Severity": 0
                }])
                
                df = pd.concat([df, new_appointment], ignore_index=True)
                save_csv(df, "appointments")
                
                st.success("✅ Regular appointment scheduled successfully!")
                st.info("🔄 Added to appointment queue (FIFO)")
    
    # Book Emergency Appointment
    with tab2:
        st.subheader("Schedule Emergency Appointment (Max Heap - Priority)")
        
        patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
        doctors_df = load_csv("doctors", ["ID","Name","Specialization","Experience","Contact","Availability"])
        
        with st.form("emergency_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                if len(patients_df) > 0:
                    patient_options = [f"{row['ID']} - {row['Name']}" for _, row in patients_df.iterrows()]
                    selected_patient = st.selectbox("Select Patient*", patient_options, key="emerg_patient")
                    patient_id = int(selected_patient.split(" - ")[0])
                else:
                    patient_id = st.number_input("Patient ID*", min_value=1, key="emerg_patient_id")
                
                appointment_date = st.date_input("Appointment Date*", key="emerg_date")
            
            with col2:
                if len(doctors_df) > 0:
                    doctor_options = [f"{row['ID']} - {row['Name']} ({row['Specialization']})" 
                                    for _, row in doctors_df.iterrows()]
                    selected_doctor = st.selectbox("Select Doctor*", doctor_options, key="emerg_doctor")
                    doctor_id = int(selected_doctor.split(" - ")[0])
                else:
                    doctor_id = st.number_input("Doctor ID*", min_value=1, key="emerg_doctor_id")
                
                appointment_time = st.time_input("Appointment Time*", key="emerg_time")
            
            severity = st.slider("Severity Level (Priority)*", 1, 10, 5, 
                               help="1 = Low Priority, 10 = Highest Priority")
            st.info(f"Priority Level: {severity}/10 - {'🔴 Critical' if severity >= 7 else '🟡 Moderate' if severity >= 4 else '🟢 Low'}")
            
            submitted = st.form_submit_button("🚨 Schedule Emergency Appointment", use_container_width=True, type="primary")
            
            if submitted:
                new_appointment = pd.DataFrame([{
                    "PatientID": patient_id,
                    "DoctorID": doctor_id,
                    "Date": str(appointment_date),
                    "Time": str(appointment_time),
                    "Type": "Emergency",
                    "Severity": severity
                }])
                
                df = pd.concat([df, new_appointment], ignore_index=True)
                save_csv(df, "appointments")
                
                st.success("✅ Emergency appointment scheduled!")
                st.info("⚡ Added to priority queue (Max Heap)")
    
    # Process Next Appointment
    with tab3:
        st.subheader("Process Next Appointment")
        st.markdown("*Processes highest priority emergency first, then regular queue*")
        
        if len(df) > 0:
            # Separate emergency and regular
            emergency_df = df[df['Type'] == 'Emergency'].sort_values('Severity', ascending=False)
            regular_df = df[df['Type'] == 'Regular']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("🚨 Emergency Queue", len(emergency_df))
                if len(emergency_df) > 0:
                    st.markdown("**Next Emergency:**")
                    next_emerg = emergency_df.iloc[0]
                    st.info(
                        f"Patient ID: {next_emerg['PatientID']}\n\n"
                        f"Doctor ID: {next_emerg['DoctorID']}\n\n"
                        f"Severity: {next_emerg['Severity']}/10\n\n"
                        f"Date: {next_emerg['Date']}\n\n"
                        f"Time: {next_emerg['Time']}"
                    )
            
            with col2:
                st.metric("📅 Regular Queue", len(regular_df))
                if len(regular_df) > 0:
                    st.markdown("**Next Regular:**")
                    next_reg = regular_df.iloc[0]
                    st.info(
                        f"Patient ID: {next_reg['PatientID']}\n\n"
                        f"Doctor ID: {next_reg['DoctorID']}\n\n"
                        f"Date: {next_reg['Date']}\n\n"
                        f"Time: {next_reg['Time']}"
                    )
            
            st.markdown("---")
            
            if st.button("▶️ Process Next Appointment", use_container_width=True, type="primary"):
                if len(emergency_df) > 0:
                    # Process emergency (extract max from heap)
                    processed = emergency_df.iloc[0]
                    df = df.drop(emergency_df.index[0])
                    
                    st.success(
                        f"✅ **EMERGENCY PROCESSED**\n\n"
                        f"Patient ID: {processed['PatientID']}\n\n"
                        f"Doctor ID: {processed['DoctorID']}\n\n"
                        f"Severity: {processed['Severity']}/10\n\n"
                        f"Time: {processed['Time']}"
                    )
                elif len(regular_df) > 0:
                    # Process regular (dequeue from FIFO)
                    processed = regular_df.iloc[0]
                    df = df.drop(regular_df.index[0])
                    
                    st.success(
                        f"✅ **REGULAR APPOINTMENT PROCESSED**\n\n"
                        f"Patient ID: {processed['PatientID']}\n\n"
                        f"Doctor ID: {processed['DoctorID']}\n\n"
                        f"Time: {processed['Time']}"
                    )
                else:
                    st.warning("⚠️ No appointments in queue!")
                
                save_csv(df, "appointments")
                st.rerun()
        else:
            st.info("📋 No appointments scheduled")
    
    # Appointment Overview
    with tab4:
        st.subheader("Appointment Schedule Overview")
        
        if len(df) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Appointments", len(df))
            with col2:
                emergency_count = len(df[df['Type'] == 'Emergency'])
                st.metric("Emergency", emergency_count)
            with col3:
                regular_count = len(df[df['Type'] == 'Regular'])
                st.metric("Regular", regular_count)
            
            st.markdown("---")
            
            # Severity distribution for emergencies
            emergency_df = df[df['Type'] == 'Emergency']
            if len(emergency_df) > 0:
                fig = px.histogram(
                    emergency_df,
                    x='Severity',
                    title='Emergency Appointment Severity Distribution',
                    labels={'Severity': 'Severity Level', 'count': 'Number of Appointments'},
                    nbins=10,
                    color_discrete_sequence=['#ef4444']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("All Appointments")
            
            # Color code by type
            styled_df = df.style.apply(
                lambda x: ['background-color: #fee2e2' if x['Type'] == 'Emergency' 
                          else 'background-color: #dbeafe' for _ in x],
                axis=1
            )
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📋 No appointments scheduled")

# =========================
# 7. EMERGENCY CASES
# =========================
elif menu == "🚨 Emergency Cases":
    st.title("🚨 Emergency Case Management")
    st.markdown("### Max Heap priority queue for critical cases")
    
    df = load_csv("emergencies", ["PatientID","Symptoms","Severity","Time"])
    
    tab1, tab2, tab3 = st.tabs([
        "🆘 Register Emergency",
        "🏥 Attend Critical Case",
        "📋 All Emergency Cases"
    ])
    
    # Register Emergency
    with tab1:
        st.subheader("Register Emergency Case")
        
        patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
        
        with st.form("register_emergency_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                if len(patients_df) > 0:
                    patient_options = [f"{row['ID']} - {row['Name']}" for _, row in patients_df.iterrows()]
                    selected_patient = st.selectbox("Select Patient*", patient_options)
                    patient_id = int(selected_patient.split(" - ")[0])
                else:
                    patient_id = st.number_input("Patient ID*", min_value=1)
                
                symptoms = st.text_area("Emergency Symptoms*", 
                                       placeholder="Describe critical symptoms...")
            
            with col2:
                severity = st.slider("Criticality Level*", 1, 10, 5,
                                   help="1 = Minor, 10 = Life-threatening")
                
                arrival_time = st.time_input("Arrival Time*")
            
            # Severity indicator
            if severity >= 8:
                st.error(f"🔴 **CRITICAL** - Level {severity}/10")
            elif severity >= 5:
                st.warning(f"🟡 **SERIOUS** - Level {severity}/10")
            else:
                st.info(f"🟢 **STABLE** - Level {severity}/10")
            
            submitted = st.form_submit_button("🚨 Register Emergency", use_container_width=True, type="primary")
            
            if submitted and symptoms:
                new_emergency = pd.DataFrame([{
                    "PatientID": patient_id,
                    "Symptoms": symptoms,
                    "Severity": severity,
                    "Time": str(arrival_time)
                }])
                
                df = pd.concat([df, new_emergency], ignore_index=True)
                # Sort by severity (Max Heap behavior)
                df = df.sort_values('Severity', ascending=False).reset_index(drop=True)
                save_csv(df, "emergencies")
                
                st.success(f"✅ Emergency case registered with priority {severity}/10")
                st.info("⚡ Added to priority queue (Max Heap)")
    
    # Attend Critical Case
    with tab2:
        st.subheader("Attend Next Critical Patient")
        st.markdown("*Extract maximum severity from heap*")
        
        if len(df) > 0:
            # Most critical case (root of max heap)
            most_critical = df.iloc[0]
            
            st.error("🚨 **MOST CRITICAL CASE**")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### Patient ID: {most_critical['PatientID']}")
                st.markdown(f"**Criticality Level:** {most_critical['Severity']}/10")
                st.markdown(f"**Symptoms:** {most_critical['Symptoms']}")
                st.markdown(f"**Arrival Time:** {most_critical['Time']}")
                
                # Get patient details if available
                patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
                patient_info = patients_df[patients_df['ID'] == most_critical['PatientID']]
                
                if len(patient_info) > 0:
                    patient = patient_info.iloc[0]
                    st.markdown("---")
                    st.markdown("**Patient Details:**")
                    st.markdown(f"Name: {patient['Name']}")
                    st.markdown(f"Age: {patient['Age']}")
                    st.markdown(f"Contact: {patient['Contact']}")
            
            with col2:
                if st.button("✅ Mark as Treated", use_container_width=True, type="primary"):
                    # Remove from heap (extract max)
                    df = df.iloc[1:].reset_index(drop=True)
                    save_csv(df, "emergencies")
                    
                    st.success("✅ Patient treated and removed from emergency queue!")
                    st.rerun()
                
                st.markdown("---")
                st.metric("Remaining Cases", len(df) - 1)
        else:
            st.success("🎉 No emergency cases pending!")
    
    # All Emergency Cases
    with tab3:
        st.subheader("All Emergency Cases (Sorted by Severity)")
        
        if len(df) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Cases", len(df))
            with col2:
                critical = len(df[df['Severity'] >= 8])
                st.metric("Critical (8-10)", critical)
            with col3:
                serious = len(df[(df['Severity'] >= 5) & (df['Severity'] < 8)])
                st.metric("Serious (5-7)", serious)
            with col4:
                stable = len(df[df['Severity'] < 5])
                st.metric("Stable (1-4)", stable)
            
            st.markdown("---")
            
            # Severity visualization
            fig = px.bar(
                df,
                y='PatientID',
                x='Severity',
                orientation='h',
                title='Emergency Cases by Severity (Max Heap Order)',
                labels={'PatientID': 'Patient ID', 'Severity': 'Criticality Level'},
                color='Severity',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Display table with color coding
            def highlight_severity(row):
                if row['Severity'] >= 8:
                    return ['background-color: #fee2e2'] * len(row)
                elif row['Severity'] >= 5:
                    return ['background-color: #fef3c7'] * len(row)
                else:
                    return ['background-color: #d1fae5'] * len(row)
            
            styled_df = df.style.apply(highlight_severity, axis=1)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.download_button(
                label="📥 Download Emergency Records (CSV)",
                data=df.to_csv(index=False),
                file_name=f"emergencies_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.success("🎉 No emergency cases currently registered")

# =========================
# 8. ANALYTICS & REPORTS
# =========================
elif menu == "📊 Analytics & Reports":
    st.title("📊 Hospital Analytics & Reports")
    st.markdown("### Comprehensive system insights and statistics")
    
    # Load all data
    patients_df = load_csv("patients", ["ID","Name","Age","Gender","Contact","MedicalHistory","Symptoms"])
    doctors_df = load_csv("doctors", ["ID","Name","Specialization","Experience","Contact","Availability"])
    staff_df = load_csv("staff", ["ID","Name","Shift","Department"])
    appointments_df = load_csv("appointments", ["PatientID","DoctorID","Date","Time","Type","Severity"])
    emergencies_df = load_csv("emergencies", ["PatientID","Symptoms","Severity","Time"])
    bills_df = load_csv("bills", ["BillID","Date","Items","Total"])
    
    tab1, tab2, tab3 = st.tabs([
        "📈 System Statistics",
        "👥 Demographics",
        "💰 Financial Reports"
    ])
    
    # System Statistics
    with tab1:
        st.subheader("System Overview Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", len(patients_df))
            st.metric("Total Doctors", len(doctors_df))
        
        with col2:
            st.metric("Total Staff", len(staff_df))
            st.metric("Total Appointments", len(appointments_df))
        
        with col3:
            st.metric("Emergency Cases", len(emergencies_df))
            critical = len(emergencies_df[emergencies_df['Severity'] >= 8]) if len(emergencies_df) > 0 else 0
            st.metric("Critical Cases", critical)
        
        with col4:
            st.metric("Total Bills Generated", len(bills_df))
            total_revenue = bills_df['Total'].sum() if len(bills_df) > 0 and 'Total' in bills_df.columns else 0
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        
        st.markdown("---")
        
        # Appointment type distribution
        if len(appointments_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Appointment Distribution")
                type_counts = appointments_df['Type'].value_counts()
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Regular vs Emergency Appointments",
                    color_discrete_sequence=['#3b82f6', '#ef4444']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Doctor Specialization Distribution")
                if len(doctors_df) > 0:
                    spec_counts = doctors_df['Specialization'].value_counts()
                    fig = px.bar(
                        x=spec_counts.values,
                        y=spec_counts.index,
                        orientation='h',
                        title="Doctors by Specialization",
                        labels={'x': 'Count', 'y': 'Specialization'},
                        color=spec_counts.values,
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Demographics
    with tab2:
        st.subheader("Patient & Staff Demographics")
        
        if len(patients_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Patient Age Distribution**")
                fig = px.histogram(
                    patients_df,
                    x='Age',
                    nbins=20,
                    title="Patient Age Distribution",
                    labels={'Age': 'Age', 'count': 'Number of Patients'},
                    color_discrete_sequence=['#8b5cf6']
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("**Gender Distribution**")
                fig = px.pie(
                    patients_df,
                    names='Gender',
                    title="Gender Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No patient demographic data available")

    # =========================
    # FINANCIAL REPORTS
    # =========================
    with tab3:
        st.subheader("Financial Performance")

        if len(bills_df) > 0 and 'Total' in bills_df.columns:
            bills_df['Date'] = pd.to_datetime(bills_df['Date'], errors='coerce')
            bills_df['Day'] = bills_df['Date'].dt.date

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${bills_df['Total'].sum():,.2f}")
            with col2:
                st.metric("Average Bill", f"${bills_df['Total'].mean():,.2f}")
            with col3:
                st.metric("Highest Bill", f"${bills_df['Total'].max():,.2f}")

            st.markdown("---")

            daily = bills_df.groupby('Day')['Total'].sum().reset_index()

            fig = px.line(
                daily,
                x='Day',
                y='Total',
                title="Daily Revenue Trend",
                labels={"Day": "Date", "Total": "Revenue ($)"},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("All Billing Records")
            st.dataframe(bills_df, use_container_width=True, hide_index=True)

        else:
            st.info("No financial records available yet")

# =========================
# END OF APPLICATION
# =========================
