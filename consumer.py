import json
import torch
import pickle
import psycopg2
import numpy as np
import time
from kafka import KafkaConsumer
from alerting import send_alert
from train_models import PatientAutoencoder

# Kafka Settings
KAFKA_BROKER = 'localhost:29092' # Check karein agar aapka broker 9092 ya 29092 par hai
TOPIC_NAME = 'patient_vitals'

# 1. Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="health_monitor",
        user="health_admin",
        password="admin_password",
        port="5432"
    )

# 2. Models Load karein
def load_models():
    # Scaler load karein (Data normalization ke liye)
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    # Isolation Forest load karein (Anomaly detection ke liye)
    with open('models/isolation_forest.pkl', 'rb') as f:
        iso_forest = pickle.load(f)
        
    # Autoencoder load karein (Deep Learning pattern recognition)
    autoencoder = PatientAutoencoder(input_dim=5)
    autoencoder.load_state_dict(torch.load('models/autoencoder.pth'))
    autoencoder.eval()
    
    return scaler, iso_forest, autoencoder

# 3. AI Anomaly Score aur Severity Calculation
def calculate_anomaly_score(vitals_arr, scaler, iso_forest, autoencoder):
    vitals_scaled = scaler.transform([vitals_arr])
    
    # Isolation Forest Score (Negative value matlab anomaly)
    if_score_raw = iso_forest.decision_function(vitals_scaled)[0]
    if_score = -if_score_raw # Isse higher score matlab zyada khatra
    
    # Autoencoder Score (MSE - Reconstruction Error)
    input_tensor = torch.FloatTensor(vitals_scaled)
    with torch.no_grad():
        reconstructed = autoencoder(input_tensor)
        ae_score = torch.mean((input_tensor - reconstructed)**2).item()
        
    # Heuristic Combine: 70% Weight Autoencoder ko, 30% Isolation Forest ko
    combined_score = ae_score * 0.7 + (if_score if if_score > 0 else 0) * 2.0
    
    # Thresholds based on Combined Score
    if combined_score > 3.0:
        severity = "HIGH"
    elif combined_score > 1.0:
        severity = "MEDIUM"
    else:
        severity = "LOW"
        
    return float(combined_score), severity

# 4. Main Consumer Loop
def run_consumer():
    print("🚀 Waiting for Kafka and DB to be ready...")
    time.sleep(10) # Startup delay taaki services up ho jayein

    scaler, iso_forest, autoencoder = load_models()
    print("✅ Models loaded successfully.")
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    print("📡 Listening for patient vital messages...")

    for message in consumer:
        data = message.value
        vitals_arr = [
            data['heart_rate'],
            data['spo2'],
            data['temperature'],
            data['blood_pressure_systolic'],
            data['blood_pressure_diastolic']
        ]
        
        # AI Logic Call
        score, severity = calculate_anomaly_score(vitals_arr, scaler, iso_forest, autoencoder)
        data['anomaly_score'] = score
        data['severity'] = severity
        
        # Save to PostgreSQL
        cursor.execute(
            """
            INSERT INTO patient_vitals 
            (patient_id, timestamp, heart_rate, spo2, temperature, blood_pressure_systolic, blood_pressure_diastolic, anomaly_score, severity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (data['patient_id'], data['timestamp'], data['heart_rate'], data['spo2'], data['temperature'], 
             data['blood_pressure_systolic'], data['blood_pressure_diastolic'], data['anomaly_score'], data['severity'])
        )
        conn.commit()
        
        print(f"✅ Processed {data['patient_id']} - Score: {score:.2f} - Severity: {severity}")
        
        # 5. Advanced Alerting System Trigger
        if severity == "HIGH":
            send_alert(data['patient_id'], data, severity, score)

if __name__ == "__main__":
    run_consumer()