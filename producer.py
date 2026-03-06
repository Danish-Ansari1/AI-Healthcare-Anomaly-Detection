import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BROKER = 'localhost:29092'
TOPIC_NAME = 'patient_vitals'

def get_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def generate_vital_signs(patient_id):
    # Simulate realistic vital signs with occasional anomalies.
    is_anomaly = random.random() < 0.05 # 5% chance of anomaly
    
    if is_anomaly:
        hr = random.uniform(40, 50) if random.random() < 0.5 else random.uniform(120, 180)
        spo2 = random.uniform(70, 89)
        temp = random.uniform(39.0, 41.0)
        bp_sys = random.uniform(160, 200)
        bp_dia = random.uniform(100, 120)
    else:
        hr = random.uniform(60, 100)
        spo2 = random.uniform(95, 100)
        temp = random.uniform(36.1, 37.2)
        bp_sys = random.uniform(90, 120)
        bp_dia = random.uniform(60, 80)

    return {
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "heart_rate": round(hr, 2),
        "spo2": round(spo2, 2),
        "temperature": round(temp, 2),
        "blood_pressure_systolic": round(bp_sys, 2),
        "blood_pressure_diastolic": round(bp_dia, 2)
    }

if __name__ == "__main__":
    print(f"Starting producer... connecting to {KAFKA_BROKER}")
    while True:
        try:
            producer = get_producer()
            print("Producer connected to Kafka.")
            break
        except Exception as e:
            print(f"Waiting for Kafka... {e}")
            time.sleep(5)
    
    patient_ids = [f"PAT_{i:03d}" for i in range(1, 6)]
    
    try:
        while True:
            for pid in patient_ids:
                vitals = generate_vital_signs(pid)
                producer.send(TOPIC_NAME, vitals)
                print(f"Sent: {vitals}")
            producer.flush()
            time.sleep(2) # Send data every 2 seconds
    except KeyboardInterrupt:
        print("Stopping producer.")
    finally:
        producer.close()
