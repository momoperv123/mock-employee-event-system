from utils.logging_config import configure_logger
from utils.kafka_helpers import create_kafka_consumer
import json

logging = configure_logger()

consumer = create_kafka_consumer("employee_updates", "dlq-events")

logging.info("DLQ Consumer is live...")

for message in consumer:
    event = message.value
    logging.warning(f"[DLQ EVENT] {event}")
    with open("/data/dlq_log.jsonl", "a") as f: f.write(json.dumps(event) + "\n")
    