import os, datetime

LOG_FILE = os.path.expanduser("~/.file_helper.log")

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")
