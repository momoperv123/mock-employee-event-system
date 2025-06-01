from kafka import KafkaConsumer, KafkaProducer
import json
import time
import logging

def create_kafka_consumer(topic, group_id):
    for _ in range(10):
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers='kafka:9092',
                auto_offset_reset='earliest',
                group_id=group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
        except Exception as e:
            logging.warning(f"[RETRYING] Kafka broker not ready: {e}")
            time.sleep(3)
    raise Exception("Kafka broker not reachable after retries")

def create_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.loads(v.decode('utf-8'))
    )