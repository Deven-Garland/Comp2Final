# platform_runner.py - run platform server with fixed game registry
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / "arcade_project"))

from arcade_project.platform_server.server import run_server

ECE_HOST = "ece-000.eng.temple.edu"
PLATFORM_PORT = 50070
CPP_GAME_PORT = 50072

from arcade_project.platform_server.chat import GeminiFilter
g = GeminiFilter()
print("Gemini test:", g.is_clean("fuckkk"))

run_server(
    host="0.0.0.0",
    port=PLATFORM_PORT,
    players_per_match=1,
    game_servers=[
        # Two-server setup: all games route to one shared C++ gameplay server.
        ("mennah", ECE_HOST, CPP_GAME_PORT),
        ("deven", ECE_HOST, CPP_GAME_PORT),
        ("ellie", ECE_HOST, CPP_GAME_PORT),
        ("vraj", ECE_HOST, CPP_GAME_PORT),
        ("kimberly", ECE_HOST, CPP_GAME_PORT),
    ],
)