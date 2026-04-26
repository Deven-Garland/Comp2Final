"""
stop.py - Stop all MOSFET Arcade servers.
Run: python3 stop.py
"""

import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "logs"

print("======================================")
print("   MOSFET Arcade - Stopping Servers")
print("======================================")

pid_file = LOG_DIR / "platform_pid.txt"
if pid_file.exists():
    pid = int(pid_file.read_text().strip())
    subprocess.run(["kill", str(pid)], capture_output=True)
    pid_file.unlink()
    print(f"  Platform server (PID {pid}) stopped.")

cpp_pid_file = LOG_DIR / "cpp_pids.txt"
if cpp_pid_file.exists():
    for pid in cpp_pid_file.read_text().strip().splitlines():
        subprocess.run(["kill", pid.strip()], capture_output=True)
        print(f"  C++ server PID {pid.strip()} stopped.")
    cpp_pid_file.unlink()

subprocess.run(["pkill", "-f", "server_text"], capture_output=True)
subprocess.run(["pkill", "-f", "platform_runner"], capture_output=True)

print("  Done.")
print("======================================")