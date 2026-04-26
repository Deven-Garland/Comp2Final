"""
Benchmark core platform-server query performance using synthetic CSV data.

This tests platform data-structure/query speed directly (no network),
which matches the assignment requirement for large-scale query testing.
"""

import csv
import random
import time
from pathlib import Path
from contextlib import contextmanager


ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "synthetic_dataset"
PLAYERS_CSV = DATASET_DIR / "players.csv"
SESSIONS_CSV = DATASET_DIR / "sessions.csv"
GAMES_CSV = DATASET_DIR / "games.csv"


@contextmanager
def suspend_persistence(server):
    """
    Temporarily disable expensive JSON saves while bulk-loading benchmark data.
    Restores original behavior and flushes once at the end.
    """
    original_runtime_save = server._save_runtime_state
    original_accounts_save = server.accounts._save
    server._save_runtime_state = lambda: None
    server.accounts._save = lambda: None
    try:
        yield
    finally:
        server._save_runtime_state = original_runtime_save
        server.accounts._save = original_accounts_save
        # Persist once so benchmark runs still leave valid state files.
        server.accounts._save()
        server._save_runtime_state()


def load_game_map():
    game_map = {}
    with GAMES_CSV.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            game_id = int(row["game_id"])
            game_map[game_id] = row["game_name"].strip()
    return game_map


def load_players():
    players = {}
    with PLAYERS_CSV.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            username = (row.get("username") or "").strip()
            if not username:
                continue
            player_id = int(row["player_id"])
            players[player_id] = username
    return players


def load_sessions():
    sessions = []
    with SESSIONS_CSV.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                session = {
                    "player_id": int(row["player_id"]),
                    "game_id": int(row["game_id"]),
                    "score": int(row["score"]),
                    "duration": int(row["duration"]) if row["duration"] not in ("", None) else 0,
                }
            except (ValueError, TypeError):
                continue
            sessions.append(session)
    return sessions


def main():
    # Import here so this script can run from data/ easily.
    import sys

    project_root = ROOT.parent
    sys.path.insert(0, str(project_root))
    from platform_server.server import PlatformServer

    print("Loading CSVs...")
    game_map = load_game_map()
    players_by_id = load_players()
    sessions = load_sessions()
    print(f"Loaded players: {len(players_by_id)}")
    print(f"Loaded sessions: {len(sessions)}")
    print(f"Loaded games: {len(game_map)}")

    server = PlatformServer(players_per_match=2, game_servers=[])

    usernames = list(set(players_by_id.values()))

    print("Registering synthetic users and ingesting sessions...")
    ingest_start = time.perf_counter()
    with suspend_persistence(server):
        # Register synthetic users once (skip if already present).
        for username in usernames:
            if not server.accounts.exists(username):
                server.register(username, "bench_pw")

        for session in sessions:
            username = players_by_id.get(session["player_id"])
            game = game_map.get(session["game_id"], "global")
            if not username:
                continue
            server.record_session_result(
                game=game,
                username=username,
                score=max(0, session["score"]),
                play_time=max(0, session["duration"]),
            )
    ingest_elapsed = time.perf_counter() - ingest_start
    print(f"Ingest time: {ingest_elapsed:.2f}s")

    # Build a reproducible query set.
    random.seed(3822)
    query_games = list(game_map.values())
    query_stats = ["score", "play_time", "sessions"]

    # Timed query batch (simulates many lookups).
    total_queries = 100000
    print(f"Running {total_queries} mixed queries...")
    query_start = time.perf_counter()
    for _ in range(total_queries):
        game = random.choice(query_games)
        stat = random.choice(query_stats)
        username = random.choice(usernames)

        server.top_players(k=10, game=game, stat=stat)
        server.player_rank(username=username, game=game, stat=stat)
        server.players_in_score_range(game=game, stat=stat, low=100, high=700)
    query_elapsed = time.perf_counter() - query_start

    print("\n=== Benchmark Summary ===")
    print(f"Total query time: {query_elapsed:.2f}s")
    print(f"Avg time/query trio: {query_elapsed / total_queries * 1000:.4f} ms")
    print("Done.")


if __name__ == "__main__":
    main()
