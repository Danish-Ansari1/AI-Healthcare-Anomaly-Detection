import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(page_title="AI Health Monitor", layout="wide")

# Database connection
def get_db_connection():
    try:
        # Streamlit secrets se URL lega
        return psycopg2.connect(st.secrets["DATABASE_URL"])
    except:
        # Local testing ke liye (VS Code ke liye)
        return psycopg2.connect(os.environ.get('DATABASE_URL'))

st.title("🏥 Patient Health Anomaly Detection")

conn = get_db_connection()
if conn:
    # Sidebar filters
    st.sidebar.header("Filter Data")
    
    # Data fetch karna
    df = pd.read_sql("SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 50", conn)
    
    # Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("High Alerts", len(df[df['severity'] == 'HIGH']))
    col3.metric("Avg Heart Rate", int(df['heart_rate'].mean()))

    # Show Table
    st.subheader("Recent Vitals")
    st.dataframe(df, use_container_width=True)
    
    # Chart dikhana
    st.subheader("Heart Rate Trend")
    st.line_chart(df.set_index('timestamp')['heart_rate'])
    
    conn.close()