# app/store.py
import json
import os
from threading import Lock

STORE_FILE = "/tmp/results_store.json"   # Railway /tmp persists within a session
_lock = Lock()

def _load() -> dict:
    if os.path.exists(STORE_FILE):
        try:
            with open(STORE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save(data: dict):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f)

def save_result(key: str, value: dict):
    with _lock:
        data = _load()
        data[key] = value
        _save(data)

def get_all_results() -> list:
    with _lock:
        data = _load()
        return list(data.values())
    
    # app/store.py — add these alongside your existing save_result()

_active_calls: set[str] = set()

def set_call_active(key: str):
    _active_calls.add(key)

def set_call_inactive(key: str):
    _active_calls.discard(key)

def is_call_active(key: str) -> bool:
    return key in _active_calls
