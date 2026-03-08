import streamlit as st
import pandas as pd
import psycopg2
import os

# 1. Page Config
st.set_page_config(page_title="AI Health Monitor", layout="wide", page_icon="🏥")

# 2. Database Connection Function
def get_db_connection():
    try:
        # Pehle st.secrets check karega (Cloud ke liye), phir os.environ (Local ke liye)
        conn_str = st.secrets.get("DATABASE_URL") or os.environ.get('DATABASE_URL')
        if not conn_str:
            return None
        return psycopg2.connect(conn_str)
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

# 3. Table Creation Function (Jo table missing thi, ye use bana dega)
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
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Table banane mein error: {e}")

# Database initialize karein
init_db()

st.title("🏥 Patient Health Anomaly Detection")

conn = get_db_connection()
if conn:
    st.sidebar.header("Filter Data")
    
    try:
        # 4. Data Fetch Karna
        df = pd.read_sql("SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 50", conn)
        
        if not df.empty:
            # 5. Dashboard Metrics (Safe Calculations)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", len(df))
            
            # Severity check (agar column missing ho toh crash nahi hoga)
            high_alerts = len(df[df['severity'] == 'HIGH']) if 'severity' in df.columns else 0
            col2.metric("High Alerts", high_alerts)
            
            avg_hr = int(df['heart_rate'].mean()) if 'heart_rate' in df.columns else 0
            col3.metric("Avg Heart Rate", f"{avg_hr} BPM")

            # 6. Show Table
            st.subheader("📋 Recent Vitals")
            st.dataframe(df, use_container_width=True)
            
            # 7. Chart (Timestamp check)
            st.subheader("📈 Heart Rate Trend")
            if 'timestamp' in df.columns and not df['timestamp'].isnull().all():
                st.line_chart(df.set_index('timestamp')['heart_rate'])
        else:
            st.info("ℹ️ Database connected hai, par abhi koi data nahi hai. Niche button daba kar test data daalein.")
            if st.button("➕ Add Test Data"):
                cur = conn.cursor()
                cur.execute("INSERT INTO patient_vitals (patient_name, heart_rate, blood_pressure, temperature, severity) VALUES ('Test Patient', 75, '120/80', 98.6, 'NORMAL')")
                conn.commit()
                st.success("Test data add ho gaya! Page refresh ho raha hai...")
                st.rerun()

    except Exception as e:
        st.error(f"⚠️ Data Error: {e}")
    
    finally:
        conn.close()
else:
    st.warning("⚠️ Database connection nahi mil raha. Apne Streamlit Secrets aur Database URL check karein.")
