import json
import uuid
import time
from datetime import datetime
from pathlib import Path


RUNS_DIR = Path("runs")
RUNS_DIR.mkdir(exist_ok=True)


def generate_run_id():
    return str(uuid.uuid4())


def log_run(run_id, data):
    file_path = RUNS_DIR / f"{run_id}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def get_timestamp():
    return datetime.utcnow().isoformat()