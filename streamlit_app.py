import streamlit as st
import pandas as pd
import psycopg2
import os

# Database Connection function with SSL support
def get_db_connection():
    try:
        conn_str = st.secrets.get("DATABASE_URL") or os.environ.get('DATABASE_URL')
        return psycopg2.connect(conn_str)
    except Exception as e:
        st.error(f"❌ Connection Fail: {e}")
        return None

# Table automatically banane ke liye
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patient_vitals (
                id SERIAL PRIMARY KEY,
                patient_name TEXT,
                heart_rate INTEGER,
                blood_pressure TEXT,
                temperature FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

init_db() # App start hote hi table check karega

st.title("🏥 Patient Health Dashboard")
# ... baki ka dashboard code
