import json
from pathlib import Path

MEMORY_FILE = Path("agent_memory.json")


class MemoryStore:
    def __init__(self):
        if not MEMORY_FILE.exists():
            self._write({
                "preferences": {
                    "food_budget": 120,
                    "max_food_eta": 25,
                    "travel_preference": "fastest"
                },
                "history": []
            })

    def _read(self):
        return json.loads(MEMORY_FILE.read_text())

    def _write(self, data):
        MEMORY_FILE.write_text(json.dumps(data, indent=2))

    def get_preferences(self):
        return self._read()["preferences"]

    def log_execution(self, record):
        data = self._read()
        data["history"].append(record)
        self._write(data)
