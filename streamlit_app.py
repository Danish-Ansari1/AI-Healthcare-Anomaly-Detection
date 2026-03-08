import streamlit as st
import pandas as pd
import psycopg2
import os

# Page Configuration
st.set_page_config(page_title="AI Health Monitor", layout="wide", page_icon="🏥")

# 1. Database Connection Function
def get_db_connection():
    try:
        # Pehle secrets se check karega, phir environment variables se
        conn_string = st.secrets.get("DATABASE_URL") or os.environ.get('DATABASE_URL')
        return psycopg2.connect(conn_string)
    except Exception as e:
        st.error(f"Database se connect nahi ho paye: {e}")
        return None

# 2. Table Banane Wala Function (Agar table nahi hai toh bana dega)
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
                severity TEXT DEFAULT 'NORMAL',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

# Database setup karein
init_db()

st.title("🏥 Patient Health Anomaly Detection")

conn = get_db_connection()
if conn:
    # 3. Data Fetch Karna
    try:
        query = "SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 50"
        df = pd.read_sql(query, conn)
        
        if df.empty:
            st.warning("Database connected hai, lekin abhi koi data nahi hai. Naya data daalein!")
        else:
            # Simple AI Anomaly Logic: Agar Heart Rate 100 se upar hai toh 'HIGH' alert
            # (Ye code aapke metrics ko crash hone se bachayega)
            df['severity'] = df['heart_rate'].apply(lambda x: 'HIGH' if x > 100 or x < 60 else 'NORMAL')

            # 4. Dashboard Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", len(df))
            col2.metric("High Alerts", len(df[df['severity'] == 'HIGH']))
            col3.metric("Avg Heart Rate", f"{int(df['heart_rate'].mean())} BPM")

            # 5. Show Table
            st.subheader("📋 Recent Patient Vitals")
            st.dataframe(df, use_container_width=True)
            
            # 6. Chart Dikhana
            st.subheader("📈 Heart Rate Trend")
            if 'timestamp' in df.columns:
                chart_data = df.set_index('timestamp')['heart_rate']
                st.line_chart(chart_data)

    except Exception as e:
        st.error(f"Data load karne mein error: {e}")
    
    finally:
        conn.close()
else:
    st.error("Database connection fail ho gaya. Please check your Secrets!")
