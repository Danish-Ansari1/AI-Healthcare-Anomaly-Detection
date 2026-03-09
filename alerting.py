import logging
import json
import time

# Logging configuration: This will make Docker logs parseable.
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("AlertSystem")

def send_alert(patient_id, vitals, severity, anomaly_score):
    """
    Advanced Alerting: Console warning + Docker JSON Event Message.
    """
    # An alert will be triggered only for HIGH severity
    if severity != "HIGH":
        return

    # 1. Structured Data for Docker Monitoring
    # This message can be filtered using ‘docker logs | grep DOCKER_EVENT’
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

    # Future integration: Here you can add Email/SMS/Webhook logic
