import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="AI Healthcare Dashboard", layout="wide")

# --- 2. DATABASE CONNECTION ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    try:
        if db_url:
            return psycopg2.connect(db_url)
        else:
            # Local connection for testing
            return psycopg2.connect(
                host="localhost",
                database="health_monitor",
                user="health_admin",
                password="admin_password",
                port="5432"
            )
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# --- 3. STREAMLIT UI ---
st.title("🏥 AI Healthcare Anomaly Detection Dashboard")

# Sidebar for Navigation
menu = ["Dashboard", "Patients List", "Add Patient", "Settings"]
choice = st.sidebar.selectbox("Menu", menu)

conn = get_db_connection()

if choice == "Dashboard":
    st.subheader("Live Vitals & Stats")
    
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Stats fetch karna
        cur.execute("SELECT COUNT(DISTINCT patient_id) FROM patient_vitals")
        total_pts = cur.fetchone()['count']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Patients", total_pts)
        col2.metric("High Alerts", "Check Logs", delta_color="inverse")
        
        # Vitals Table
        st.write("### Recent Vitals Data")
        cur.execute("SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 10")
        data = cur.fetchall()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No vitals data found.")
        cur.close()
        conn.close()

elif choice == "Patients List":
    st.subheader("Registered Patients")
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM patients ORDER BY id DESC")
        patients = cur.fetchall()
        if patients:
            st.table(pd.DataFrame(patients))
        else:
            st.warning("No patients registered yet.")
        cur.close()
        conn.close()

elif choice == "Add Patient":
    st.subheader("Register New Patient")
    with st.form("patient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        condition = st.text_area("Medical Condition")
        submit = st.form_submit_button("Add Patient")
        
        if submit and conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO patients (name, age, condition, room, gender) VALUES (%s, %s, %s, %s, %s)",
                (name, age, condition, "TBD", "Unknown")
            )
            conn.commit()
            st.success("Patient added successfully!")
            cur.close()
            conn.close()

elif choice == "Settings":
    st.subheader("System Settings")
    st.write("Database URL:", os.environ.get('DATABASE_URL', 'Not Set (Using Local)'))
