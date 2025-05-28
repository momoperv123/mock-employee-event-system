import logging
from kafka import KafkaConsumer
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def create_consumer():
    for _ in range(10):
        try:
            return KafkaConsumer(
                'employee_dlq',
                bootstrap_servers='kafka:9092',
                auto_offset_reset='earliest',
                group_id='dlq-monitor',
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
        except Exception as e:
            logging.warning(f"[RETRYING] Kafka broker not ready yet: {e}")
            time.sleep(3)
    raise Exception("Kafka broker not reachable after retries.")

consumer = create_consumer()

logging.info("DLQ Consumer is live...")

for message in consumer:
    event = message.value
    logging.warning(f"[DLQ EVENT] {event}")
    with open("/data/dlq_log.jsonl", "a") as f: f.write(json.dumps(event) + "\n")
    