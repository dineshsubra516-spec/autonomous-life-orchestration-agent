import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Use absolute path relative to this file's location
MEMORY_FILE = Path(__file__).parent.parent.parent / "agent_memory.json"


class MemoryStore:
    def __init__(self):
        if not MEMORY_FILE.exists():
            self._write({
                "user_preferences": {
                    "location": "Indiranagar, Bangalore",
                    "food_budget": 200,
                    "cuisine_preferences": ["South Indian", "Fast Food"],
                    "class_start_time": "09:00",
                    "class_location": "IIT Madras",
                    "timezone": "Asia/Kolkata"
                },
                "execution_history": []
            })

    def _read(self) -> Dict[str, Any]:
        """Read memory file"""
        try:
            return json.loads(MEMORY_FILE.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_memory()

    def _write(self, data: Dict[str, Any]) -> None:
        """Write memory file"""
        MEMORY_FILE.write_text(json.dumps(data, indent=2, default=str))

    def _get_default_memory(self) -> Dict[str, Any]:
        """Get default memory structure"""
        return {
            "user_preferences": {
                "location": "Indiranagar, Bangalore",
                "food_budget": 200,
                "cuisine_preferences": ["South Indian", "Fast Food"],
                "class_start_time": "09:00",
                "class_location": "IIT Madras",
                "timezone": "Asia/Kolkata"
            },
            "execution_history": []
        }

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        data = self._read()
        return data.get("user_preferences", {})

    def save_user_preferences(self, prefs: Dict[str, Any]) -> None:
        """Save user preferences"""
        data = self._read()
        data["user_preferences"] = prefs
        self._write(data)

    def log_execution(self, record: Dict[str, Any]) -> None:
        """Log an execution record"""
        data = self._read()
        history = data.get("execution_history", [])
        
        record["timestamp"] = datetime.now().isoformat()
        history.append(record)
        
        # Keep only last 50 records
        data["execution_history"] = history[-50:]
        self._write(data)

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history"""
        data = self._read()
        history = data.get("execution_history", [])
        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        history = self.get_execution_history(limit=100)
        
        total_executions = len(history)
        successful = len([h for h in history if h.get("confidence", 0) >= 0.6])
        average_confidence = (
            sum(h.get("confidence", 0) for h in history) / len(history)
            if history else 0
        )
        
        return {
            "total_executions": total_executions,
            "successful": successful,
            "success_rate": (successful / total_executions * 100) if total_executions else 0,
            "average_confidence": round(average_confidence, 2)
        }

