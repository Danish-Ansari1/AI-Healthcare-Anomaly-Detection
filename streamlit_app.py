import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="AI Health Monitor", layout="wide")

# 1. Database Connection Function
def get_db_connection():
    try:
        conn_str = st.secrets.get("DATABASE_URL") or os.environ.get('DATABASE_URL')
        return psycopg2.connect(conn_str)
    except Exception as e:
        st.error(f"Database connection fail: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
        
            cur.execute("""
                CREATE TABLE IF NOT EXISTS patient_vitals (
                    id SERIAL PRIMARY KEY,
                    patient_name TEXT,
                    heart_rate INTEGER,
                    blood_pressure TEXT,
                    temperature FLOAT,
                    severity TEXT DEFAULT 'NORMAL',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("SELECT COUNT(*) FROM patient_vitals")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO patient_vitals (patient_name, heart_rate, blood_pressure, temperature) VALUES ('Patient 1', 75, '120/80', 98.6)")
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Table setup error: {e}")


init_db()

st.title("🏥 Patient Health Anomaly Detection")

# 3. Data Display Logic
conn = get_db_connection()
if conn:
    try:
        df = pd.read_sql("SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 50", conn)
        if not df.empty:
            st.metric("Total Records", len(df))
            st.dataframe(df, use_container_width=True)
            st.line_chart(df.set_index('timestamp')['heart_rate'])
        else:
            st.info("Database connected! Refresh karein data dikhne lagega.")
    finally:
        conn.close()
