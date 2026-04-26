# platform_runner.py - launched by start.py to run the platform server
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / "arcade_project"))

from arcade_project.platform_server.server import run_server

run_server(
    host="0.0.0.0",
    port=50070,
    players_per_match=1,
    game_servers=[
        ("mennah",   "ece-000.eng.temple.edu", 50063),
        ("deven",    "ece-000.eng.temple.edu", 50064),
        ("ellie",    "ece-000.eng.temple.edu", 50072),
        ("vraj",     "ece-000.eng.temple.edu", 50077),
        ("kimberly", "ece-000.eng.temple.edu", 50081),
    ],
)