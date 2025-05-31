from utils.logging_config import *
from utils.kafka_helpers import *
from utils.metrics import *
import json

logging_config()

consumer = create_kafka_consumer()

logging.info("DLQ Consumer is live...")

for message in consumer:
    event = message.value
    logging.warning(f"[DLQ EVENT] {event}")
    with open("/data/dlq_log.jsonl", "a") as f: f.write(json.dumps(event) + "\n")
    