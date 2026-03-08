from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    # Render par hum 'DATABASE_URL' Environment Variable set karenge
    db_url = os.environ.get('DATABASE_URL')
    
    try:
        if db_url:
            # Online Database (Neon.tech) se connect karega
            return psycopg2.connect(db_url)
        else:
            # Aapke local computer ke liye fallback
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
    """Main Dashboard Page"""
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    """Alerts History Page"""
    return render_template('alerts.html')

@app.route('/patients')
def patients_page():
    """Database se patients fetch karke page par dikhana"""
    conn = get_db_connection()
    if not conn:
        return render_template('patients.html', patients=[], error="Database Connection Failed")
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Check karein ki table exist karti hai ya nahi
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

# --- 3. API ROUTES ---

@app.route('/api/add_patient', methods=['POST'])
def add_patient():
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

# --- 4. START SERVER ---

if __name__ == "__main__":
    # Render automatic 'PORT' environment variable deta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
