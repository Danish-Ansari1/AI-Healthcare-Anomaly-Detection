from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    # Render Dashboard se 'DATABASE_URL' uthayega
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        return psycopg2.connect(db_url)
    else:
        return psycopg2.connect(
            host="localhost",
            database="health_monitor",
            user="health_admin",
            password="admin_password",
            port="5432"
        )

# --- 2. FRONTEND ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    return render_template('alerts.html')

@app.route('/patients')
def patients_page():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM patients ORDER BY id DESC")
        patients_list = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('patients.html', patients=patients_list)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('patients.html', patients=[])

@app.route('/settings')
def settings():
    return render_template('settings.html')

# --- 3. API ROUTES ---

@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    data = request.get_json()
    name, age, cond = data.get('name'), data.get('age'), data.get('condition')
    if not name or not age or not cond:
        return jsonify({"status": "error", "message": "Missing data"}), 400
    try:
        conn = get_db_connection()
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

@app.route('/api/vitals')
def get_vitals():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT patient_id, timestamp, heart_rate, spo2, temperature, 
                   blood_pressure_systolic AS bp_sys, 
                   blood_pressure_diastolic AS bp_dia, severity
            FROM patient_vitals ORDER BY timestamp DESC LIMIT 50
        ''')
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
        total_pts = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'HIGH'")
        high = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'MEDIUM'")
        med = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'data': {'total_pts': total_pts or 0, 'high_alerts': high or 0, 'med_alerts': med or 0}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- 4. START SERVER ---

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
