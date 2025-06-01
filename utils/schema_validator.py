import json
import os
from jsonschema import validate, ValidationError

def load_schema(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return None

schema = load_schema("schemas/employee_update_schema.json")

def validate_event(event):
    try:
        validate(instance=event, schema=schema)
        return True, None
    except ValidationError as ve: return False, str(ve)