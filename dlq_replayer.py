import json
from kafka import KafkaProducer
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

DLQ_LOG_PATH = "/data/dlq_log.jsonl"
REPLAYED_PATH = "/data/dlq_replayed.jsonl"

replayed_hashes = set()
if os.path.exists(REPLAYED_PATH):
    with open(REPLAYED_PATH, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                key = json.dumps(event["original_event"], sort_keys=True)
                replayed_hashes.add(hash(key))
            except Exception: continue

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

if __name__ == "__main__":
    with open(DLQ_LOG_PATH, 'r') as f: dlq_events = [json.loads(line) for line in f if line.strip()]
    with open(REPLAYED_PATH, 'a') as replayed_file:
        for event in dlq_events:
            original_event = event["original_event"]
            key = json.dumps(original_event, sort_keys=True)
            if hash(key) in replayed_hashes:
                logging.info(f"[DLQ REPLAYER] Skipping already replayed event: {original_event}")
                continue
            producer.send("employee_updates", value=original_event)
            replayed_file.write(json.dumps(event) + "\n")
            logging.info(f"[DLQ REPLAYER] Replayed event: {event}")
    producer.flush()