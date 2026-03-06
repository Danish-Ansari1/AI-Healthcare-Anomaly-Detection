import logging
import json
import time

# Logging configuration: Isse Docker logs parseable banenge
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AlertSystem")

def send_alert(patient_id, vitals, severity, anomaly_score):
    """
    Advanced Alerting: Console warning + Docker JSON Event Message.
    """
    # Sirf HIGH severity par alert trigger hoga
    if severity != "HIGH":
        return

    # 1. Structured Data for Docker Monitoring
    # Is message ko 'docker logs | grep DOCKER_EVENT' se filter kiya ja sakta hai
    alert_payload = {
        "event_type": "CRITICAL_ANOMALY",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "patient_id": patient_id,
        "severity": severity,
        "anomaly_score": round(float(anomaly_score), 4),
        "vitals": vitals
    }

    # 2. Console (Visual) Warning for Debugging
    print("\n" + "!"*60)
    print(f" 🚨 [DOCKER_EVENT] {json.dumps(alert_payload)}") # JSON message for Docker logs
    print("!"*60)

    logger.warning("="*60)
    logger.warning("  🔴 IMMEDIATE MEDICAL ATTENTION REQUIRED 🔴  ")
    logger.warning(f"  Patient ID : {patient_id}")
    logger.warning(f"  AI Score   : {anomaly_score:.4f}")
    logger.warning(f"  Status     : {severity}")
    logger.warning(f"  Condition  : Critical Vitals Detected")
    logger.warning(f"  Action     : Dispatching Emergency Response...")
    logger.warning("="*60 + "\n")

    # Future integration: Yahan aap Email/SMS/Webhook logic add kar sakte hain