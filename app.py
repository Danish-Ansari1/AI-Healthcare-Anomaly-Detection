from flask import Flask, render_template, jsonify, request 
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    
    try:
        if db_url:
            return psycopg2.connect(db_url)
        else:
            # Local Fallback 
            return psycopg2.connect(
                host="localhost",
                database="health_monitor",
                user="health_admin",
                password="admin_password",
                port="5432"
            )
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

# --- 2. FRONTEND ROUTES ---

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/patients')
def patients_page():
    conn = get_db_connection()
    if not conn:
        return render_template('patients.html', patients=[], error="Database Connection Failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM patients ORDER BY id DESC")
        patients_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('patients.html', patients=patients_list)
    except Exception as e:
        print(f"Error fetching patients: {e}")
        return render_template('patients.html', patients=[])

@app.route('/settings')
def settings():
    return render_template('settings.html')

# --- 3. API ROUTES (Data for Dashboard) ---

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    if not conn: 
        return jsonify({"status": "error", "message": "DB Connection Fail"}), 500
    
    try:
        cur = conn.cursor()
        
        # 1. Total Patients
        cur.execute("SELECT COUNT(*) FROM patients")
        total_patients = cur.fetchone()[0]
        
        # 2. Critical Alerts
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'Critical'")
        critical_alerts = cur.fetchone()[0]
        
        # 3. Warnings
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'Warning'")
        warnings = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "total_patients": total_patients,
            "critical_alerts": critical_alerts,
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vitals')
def get_vitals():
    conn = get_db_connection()
    if not conn: return jsonify({"status": "error"}), 500
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT patient_id, timestamp, heart_rate, spo2, temperature, 
                   blood_pressure_systolic AS bp_sys, 
                   blood_pressure_diastolic AS bp_dia, severity
            FROM patient_vitals ORDER BY timestamp DESC LIMIT 50
        ''')
        vitals = cur.fetchall()
        for v in vitals:
            if v['timestamp']:
                v['timestamp'] = v['timestamp'].strftime('%H:%M:%S')
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'data': vitals})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    # 'request' ab properly kaam karega
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    cond = data.get('condition')

    if not name or not age or not cond:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"status": "error", "message": "DB Connection Fail"}), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patients (name, age, condition, room, gender) VALUES (%s, %s, %s, %s, %s)",
            (name, age, cond, "TBD", "Unknown")
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Patient added!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 4. START SERVER ---

if __name__ == "__main__":
   # Variable defined here so it works local and on cloud
   port = int(os.environ.get("PORT", 5000))
   app.run(host='0.0.0.0', port=port, debug=True)