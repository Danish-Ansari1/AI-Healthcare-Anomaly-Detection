CREATE TABLE IF NOT EXISTS patient_vitals (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50),
    timestamp TIMESTAMP,
    heart_rate FLOAT,
    spo2 FLOAT,
    temperature FLOAT,
    blood_pressure_systolic FLOAT,
    blood_pressure_diastolic FLOAT,
    anomaly_score FLOAT,
    severity VARCHAR(20)
);

CREATE INDEX IF NOT EXISTS idx_patient_vitals_timestamp ON patient_vitals (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_patient_vitals_patient_id ON patient_vitals (patient_id);
