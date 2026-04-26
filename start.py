"""
start.py - Start the MOSFET Arcade on the ECE server.
Run: python3 start.py
Teammates on their laptops just run: python3 client.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ECE_HOST = "ece-000.eng.temple.edu"
PLATFORM_PORT = 9000
SCRIPT_DIR = Path(__file__).resolve().parent
CPP_DIR = SCRIPT_DIR / "arcade_project" / "cpp_server"
LOG_DIR = SCRIPT_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)

print("======================================")
print("   MOSFET Arcade - Server Start")
print("======================================")
print(f"Host: {ECE_HOST}")
print(f"Platform port: {PLATFORM_PORT}")
print()

# 1. Build C++ game server
print("[1/3] Building C++ game server...")
result = subprocess.run(
    ["make", "SERIALIZER=TEXT"],
    cwd=CPP_DIR,
    stdout=open(LOG_DIR / "make.log", "w"),
    stderr=subprocess.STDOUT,
)
if result.returncode != 0:
    print("ERROR: C++ build failed. Check logs/make.log")
    sys.exit(1)
print("      Done.")

# 2. Start C++ game servers
print("[2/3] Starting C++ game servers...")
binary = CPP_DIR / "server_text"
cpp_pids = []

subprocess.run(["pkill", "-f", "server_text"], capture_output=True)
time.sleep(0.3)

for game in ("mennah", "deven", "ellie", "vraj", "kimberly"):
    log = open(LOG_DIR / f"{game}.log", "a")
    proc = subprocess.Popen(
        ["nohup", str(binary), "--game", game],
        cwd=CPP_DIR,
        stdout=log,
        stderr=log,
    )
    cpp_pids.append(proc.pid)
    print(f"      {game} -> PID {proc.pid}")
    time.sleep(0.12)

(LOG_DIR / "cpp_pids.txt").write_text("\n".join(str(p) for p in cpp_pids))
print("      Done.")

# 3. Start platform server
print(f"[3/3] Starting platform server on {ECE_HOST}:{PLATFORM_PORT}...")

subprocess.run(["pkill", "-f", "platform_runner"], capture_output=True)
time.sleep(0.2)

env = {
    **os.environ,
    "PYTHONPATH": f"{SCRIPT_DIR}:{SCRIPT_DIR / 'arcade_project'}:" + os.environ.get("PYTHONPATH", ""),
}

platform_log = open(LOG_DIR / "platform.log", "w")
proc = subprocess.Popen(
    ["nohup", sys.executable, str(SCRIPT_DIR / "platform_runner.py")],
    stdout=platform_log,
    stderr=platform_log,
    cwd=str(SCRIPT_DIR),
    env=env,
)
(LOG_DIR / "platform_pid.txt").write_text(str(proc.pid))
print(f"      PID {proc.pid}")

time.sleep(1)

log_contents = (LOG_DIR / "platform.log").read_text()
if "listening" in log_contents:
    print("      Platform server confirmed running!")
else:
    print("      WARNING: platform may have failed. Check logs/platform.log")
    print(log_contents)

print()
print("======================================")
print("  All servers running!")
print("  Teammates: just run python3 client.py")
print(f"  Logs in: {LOG_DIR}/")
print("  To stop: python3 stop.py")
print("======================================")