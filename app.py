from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# --- DATABASE CONNECTION & AUTO-INIT ---
def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

# Ye function app chalte hi tables bana dega
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY, 
                name TEXT, age INT, 
                condition TEXT, 
                room TEXT DEFAULT 'TBD', 
                gender TEXT DEFAULT 'Unknown'
            );
            CREATE TABLE IF NOT EXISTS patient_vitals (
                patient_id INT, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                heart_rate FLOAT, 
                spo2 FLOAT, 
                temperature FLOAT, 
                blood_pressure_systolic FLOAT, 
                blood_pressure_diastolic FLOAT, 
                severity TEXT
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database Tables Ready!")
    except Exception as e:
        print(f"Database Init Error: {e}")

# App start hone par init chalaein
with app.app_context():
    init_db()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vitals')
def get_vitals():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM patient_vitals ORDER BY timestamp DESC LIMIT 50")
        vitals = cur.fetchall()
        for v in vitals:
            if v['timestamp']: v['timestamp'] = v['timestamp'].strftime('%H:%M:%S')
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'data': vitals})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT patient_id) FROM patient_vitals")
        total_pts = cur.fetchone()[0] or 0
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'data': {'total_pts': total_pts}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
