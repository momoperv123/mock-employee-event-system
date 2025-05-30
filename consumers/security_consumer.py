import logging
from kafka import KafkaConsumer, KafkaProducer
import json
import random
import time
from prometheus_client import Counter, start_http_server

PROCESSED_COUNTER = Counter("processed_events_total", "Total successfully processed events", ["consumer"])
FAILURE_COUNTER = Counter("processing_failures_total", "Total processing failures", ["consumer"])
DLQ_COUNTER = Counter("dlq_events_total", "Events sent to DLQ", ["consumer"])

start_http_server(8006)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

MAX_RETRIES = 3

def process_message(update):
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if random.random() < 0.1: raise Exception("Simulated processing failure")
            logging.info(f"[SECURITY SYSTEM] Processing update for Employee ID {update['employee_id']}: {update['field_changed']} changes from '{update['old_value']}' to '{update['new_value']}'")
            PROCESSED_COUNTER.labels(consumer="security").inc()
        except Exception as e:
            FAILURE_COUNTER.labels(consumer="security").inc()
            last_exception = e
            logging.error(f"[Retry {attempt}] Failed to process message: {e}")
            time.sleep(1)
    dlq_event = {
        "original_event": update,
        "failure_reason": str(last_exception),
        "consumer": "security_consumer",
        "timestamp": time.time()
    }
    DLQ_COUNTER.labels(consumer="security").inc()
    logging.warning("[DLQ] Sending event to DLQ")
    producer.send("employee_dlq", value=dlq_event)

def create_consumer():
    for _ in range(10):
        try:
            return KafkaConsumer(
                'employee_updates',
                bootstrap_servers='kafka:9092',
                auto_offset_reset='earliest',
                group_id='security-group',
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
        except Exception as e:
            logging.warning(f"[RETRYING] Kafka broker not ready yet: {e}")
            time.sleep(3)
    raise Exception("Kafka broker not reachable after retries.")

consumer = create_consumer()

logging.info("Security Consumer listening for employee updates...")

for message in consumer:
    update = message.value
    process_message(update)