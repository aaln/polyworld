"""Importable seven-layer IR; JSON is the canonical evaluated representation."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY = json.loads((HERE / "policy.ir.json").read_text())
FINISH_ONLY = json.loads((HERE / "finish.ir.json").read_text())
