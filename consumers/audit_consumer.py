from utils.logging_config import configure_logger
from utils.kafka_helpers import create_kafka_consumer, create_kafka_producer
from utils.metrics import init_metrics
from utils.schema_validator import validate_event
import json
import random
import time

logging = configure_logger()

metrics = init_metrics(8001, "audit")
producer = create_kafka_producer()
consumer = create_kafka_consumer("employee_updates", "audit-group")

MAX_RETRIES = 3

def process_message(update):
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if random.random() < 0.1: raise Exception("Simulated failure")
            logging.info(f"[AUDIT] {update}")
            with open("/data/audit_log.json", "a") as f: f.write(json.dumps(update) + "\n")
            metrics["processed"].inc()
            return
        except Exception as e:
            metrics["failures"].inc()
            last_exception = e
            logging.error(f"[Retry {attempt}] Failed to process message: {e}")
            time.sleep(1)
    dlq_event = {
        "original_event": update,
        "failure_reason": str(last_exception),
        "consumer": "audit_consumer",
        "timestamp": time.time()
    }
    metrics["dlq"].inc()
    logging.warning("[DLQ] Sending event to DLQ")
    producer.send("employee_dlq", value=dlq_event)

logging.info("Audit Consumer listening for employee updates...")

for message in consumer:
    update = message.value
    is_valid, error = validate_event(update)
    if not is_valid:
        logging.error(f"[INVALID EVENT] {error}")
        continue
    process_message(update)