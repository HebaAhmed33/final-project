"""Wrapper to run uvicorn with unbuffered output and log capture."""
import sys
import os

# Force unbuffered
os.environ["PYTHONUNBUFFERED"] = "1"

# Redirect all print output to a log file AND console
class TeeWriter:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self):
        for s in self.streams:
            s.flush()
    def isatty(self):
        return False
    def fileno(self):
        return self.streams[0].fileno()

log_path = os.path.join(os.path.dirname(__file__), "runtime_proof.log")
log_file = open(log_path, "w", encoding="utf-8")
sys.stdout = TeeWriter(sys.__stdout__, log_file)
sys.stderr = TeeWriter(sys.__stderr__, log_file)

import uvicorn
uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="info")
