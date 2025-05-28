from kafka import KafkaProducer
import json
import time
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def create_producer():
    for _ in range(10):
        try:
            return KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except:
            print("[RETRYING] Kafka broker not ready yet...")
            time.sleep(3)
    raise Exception("Kafka broker not reachable after retries.")

producer = create_producer()

employee_db = {}

titles = [
    "Analyst",
    "Senior Analyst",
    "Software Engineer",
    "Senior Software Engineer",
    "Lead Engineer",
    "Engineering Manager",
    "Product Manager",
    "Technical Program Manager",
    "Data Engineer",
    "Data Scientist",
    "Quantitative Analyst",
    "Site Reliability Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "DevOps Engineer"
]

departments = [
    "Engineering",
    "Data",
    "Finance",
    "Product",
    "Operations",
    "Legal",
    "Security",
    "Compliance",
    "Sales",
    "Customer Support",
    "HR",
    "Marketing",
    "Infrastructure",
    "Research",
    "Trading Systems"
]

locations = [
    "New York",
    "London",
    "Tokyo",
    "Singapore",
    "San Francisco",
    "Chicago",
    "Frankfurt",
    "Toronto",
    "Hong Kong",
    "Paris",
    "Dubai",
    "São Paulo",
    "Sydney",
    "Mumbai",
    "Los Angeles"
]

def generate_employees():
    for _ in range(100):
        employee_id = random.randint(1000, 9999)
        employee_title = random.choice(titles)
        employee_dept = random.choice(departments)
        employee_loc = random.choice(locations)
        if employee_id in employee_db: continue
        employee_db[employee_id] = {
            "title": employee_title,
            "department": employee_dept,
            "location": employee_loc,
            "schema_version": 1
        }

def update_employees():
    for _ in range(100):
        employee_id = random.choice(list(employee_db.keys()))
        field, current_employee_field = random.choice(list(employee_db[employee_id].items()))
        if field == "title": new_employee_field = random.choice(titles)
        if field == "department": new_employee_field = random.choice(departments)
        if field == "location": new_employee_field = random.choice(locations)
        if new_employee_field == current_employee_field:
            logging.info(f"[UNSUCCESSFUL] Employee with ID {employee_id} {field} of {current_employee_field} has not changed")
            continue
        elif new_employee_field != current_employee_field:
            employee_db[employee_id]["schema_version"] += 1
            event = {
                "schema_version": employee_db[employee_id]["schema_version"],
                "employee_id": employee_id,
                "field_changed": field,
                "old_value": current_employee_field,
                "new_value": new_employee_field,
                "department": employee_db[employee_id]["department"],
                "timestamp": time.time()
            }
            logging.info(f"[KAFKA EVENT] {event}")
            producer.send("employee_updates", value=event)
            employee_db[employee_id][field] = new_employee_field
            logging.info(f"[SUCCESSFUL] Employee with ID {employee_id} has their {field} of {current_employee_field} updated to {new_employee_field}")
        else:
            logging.info(f"[ERROR] Employee with ID {employee_id} does not exist")

generate_employees()

while True:
    update_employees()
    time.sleep(2)