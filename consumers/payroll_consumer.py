import os
from utils.logging_config import *
from utils.kafka_helpers import *
from utils.metrics import *
import random
import json
import time

logging_config()

metrics = init_metrics(8005, "payroll-group")
producer = create_kafka_producer()
consumer = create_kafka_consumer()

if os.path.exists("/data/payroll_state.json"): 
    with open("/data/payroll_state.json", "r") as f: payroll_db = json.load(f)
else: payroll_db = {}

MAX_RETRIES = 3

def process_message(update):
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if random.random() < 0.1: raise Exception("Simulated processing failure")
            if update["field_changed"] in ["title", "location"]:
                logging.info(f"Payroll relevant update for Employee {update['employee_id']}: {update['field_changed']} changed from {update['old_value']} to {update['new_value']}")
                if update['employee_id'] not in payroll_db: payroll_db[update['employee_id']] = {update['field_changed']: update['new_value']}
                else: payroll_db[update['employee_id']][update['field_changed']] = update['new_value']
                with open("/data/payroll_state.json", "w") as f: json.dump(payroll_db, f, indent=2)
                metrics["processed"].inc()
            else: logging.info(f"Non-payroll update ignored for Employee {update['employee_id']}: {update['field_changed']} changed")
        except Exception as e:
            metrics["failures"].inc()
            last_exception = e
            logging.error(f"[Retry {attempt}] Failed to process message: {e}")
            time.sleep(1)
    dlq_event = {
        "original_event": update,
        "failure_reason": str(last_exception),
        "consumer": "payroll_consumer",
        "timestamp": time.time()
    }
    metrics["dlq"].inc()
    logging.warning("[DLQ] Sending event to DLQ")
    producer.send("employee_dlq", value=dlq_event)

logging.info("Payroll Consumer listening for employee updates...")

for message in consumer:
    update = message.value
    process_message(update)