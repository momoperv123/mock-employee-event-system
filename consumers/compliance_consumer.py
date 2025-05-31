from utils.logging_config import *
from utils.kafka_helpers import *
from utils.metrics import *
import random
import time

logging_config()

metrics = init_metrics(8002, "compliance-group")
producer = create_kafka_producer()
consumer = create_kafka_consumer()

MAX_RETRIES = 3

def process_message(update):
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if random.random() < 0.1: raise Exception("Simulated processing failure")
            if update["field_changed"] == "department": 
                logging.info(f"[COMPLIANCE] Department change: {update}")
                metrics["processed"].inc()
        except Exception as e:
            metrics["failures"].inc()
            last_exception = e
            logging.error(f"[Retry {attempt}] Failed to process message: {e}")
            time.sleep(1)
    dlq_event = {
        "original_event": update,
        "failure_reason": str(last_exception),
        "consumer": "compliance_consumer",
        "timestamp": time.time()
    }
    metrics["dlq"].inc()
    logging.warning("[DLQ] Sending event to DLQ")
    producer.send("employee_dlq", value=dlq_event)

logging.info("Compliance Consumer is live...")

for message in consumer:
    update = message.value
    process_message(update)