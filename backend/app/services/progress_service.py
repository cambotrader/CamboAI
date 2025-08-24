from __future__ import annotations
import os
from datetime import datetime
from typing import Optional

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
LOG_PATH = os.path.join(LOG_DIR, "progress.log")

os.makedirs(LOG_DIR, exist_ok=True)


def log_progress(module: str, event: str, details: Optional[str] = None) -> None:
    ts = datetime.utcnow().isoformat()
    sanitized = (details or "").replace("\n", " ").strip()
    line = f"{ts}\t{module}\t{event}\t{sanitized}\n"
    with open(LOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
        f.write(line)


def read_logs(limit: int = 500) -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    rows: list[dict] = []
    with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.readlines()[-limit:]:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                rows.append({
                    "timestamp": parts[0],
                    "module": parts[1],
                    "event": parts[2],
                    "details": parts[3] if len(parts) > 3 else "",
                })
    return rows