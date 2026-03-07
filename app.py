from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# --- DATABASE CONNECTION ---
def get_db_connection():
  return psycopg2.connect(os.environ.get('DATABASE_URL'))

# --- 1. FRONTEND ROUTES ---

@app.route('/')
def index():
    """Main Dashboard Page"""
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    """Alerts History Page"""
    return render_template('alerts.html')

@app.route('/patients')
def patients_page():
    """Database se patients ki list fetch karke page par dikhana"""
    try:
        conn = get_db_connection()
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
    """System Settings Page"""
    return render_template('settings.html')


# --- 2. API ROUTES (DATA & ACTIONS) ---

@app.route('/api/add_patient', methods=['POST'])
def add_patient():
    """Naya patient database mein save karne ke liye"""
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    condition = data.get('condition')

    if not name or not age or not condition:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patients (name, age, condition, room, gender) VALUES (%s, %s, %s, %s, %s)",
            (name, age, condition, "TBD", "Unknown")
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Patient added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/vitals')
def get_vitals():
    """Table aur Graph ke liye live data (BP Fix ke saath)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        
        cur.execute('''
            SELECT patient_id, timestamp, heart_rate, spo2, temperature, 
                   blood_pressure_systolic AS bp_sys, 
                   blood_pressure_diastolic AS bp_dia, 
                   severity
            FROM patient_vitals
            ORDER BY timestamp DESC LIMIT 50
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

@app.route('/api/stats')
def get_stats():
    """Dashboard cards ke liye counts"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(DISTINCT patient_id) FROM patient_vitals")
        total_patients = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'HIGH'")
        high_alerts = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM patient_vitals WHERE severity = 'MEDIUM'")
        med_alerts = cur.fetchone()[0]
        
        cur.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'total_pts': total_patients or 0,
                'high_alerts': high_alerts or 0,
                'med_alerts': med_alerts or 0
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
