"""
Benchmark core platform-server query performance using synthetic CSV data.

Runs entirely offline: constructs PlatformServer in-process only. No TCP listener,
no client sockets, no SSH tunnel, and no connection to platform_runner.py.
(Optionally skips writing JSON state when ARCADE_OFFLINE_BENCHMARK_NO_DISK=1.)
"""

import csv
import os
import random
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "synthetic_dataset"
PLAYERS_CSV = DATASET_DIR / "players.csv"
SESSIONS_CSV = DATASET_DIR / "sessions.csv"
GAMES_CSV = DATASET_DIR / "games.csv"


def _env_positive_int(name: str, default=None):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        v = int(raw)
        return v if v > 0 else default
    except ValueError:
        return default


def parse_int(value, default=None):
    if value is None:
        return default
    text = str(value).strip()
    if text == "" or text.lower() == "null":
        return default
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return default


def parse_timestamp(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    if text.isdigit():
        try:
            return datetime.fromtimestamp(int(text))
        except (TypeError, ValueError, OSError):
            return None

    formats = (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y %I:%M:%S %p",
        "%Y/%m/%d %H:%M",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def canonical_username(value):
    name = (value or "").strip().lower()
    if not name:
        return ""
    return "".join(ch for ch in name if ch.isalnum())


@contextmanager
def suspend_persistence(server):
    """
    Temporarily disable expensive JSON saves while bulk-loading benchmark data.
    Restores original save hooks; when ARCADE_OFFLINE_BENCHMARK_NO_DISK is truthy,
    skips the final accounts/runtime flush (default for data_ingest.py entry point).
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
        nodisk = os.environ.get("ARCADE_OFFLINE_BENCHMARK_NO_DISK", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if not nodisk:
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
            username = canonical_username(row.get("username"))
            if not username:
                continue
            player_id = parse_int(row.get("player_id"))
            if player_id is None:
                continue
            players[player_id] = username
    return players


def load_sessions():
    sessions = []
    with SESSIONS_CSV.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_id = parse_int(row.get("player_id"))
            game_id = parse_int(row.get("game_id"))
            if player_id is None or game_id is None:
                continue

            # Prefer explicit start/end timestamps if present, else fall back to legacy duration.
            start_dt = parse_timestamp(row.get("start_time"))
            end_dt = parse_timestamp(row.get("end_time"))
            if start_dt and end_dt:
                duration = int((end_dt - start_dt).total_seconds())
            else:
                duration = parse_int(row.get("duration"), 0)

            session = {
                "player_id": player_id,
                "game_id": game_id,
                "score": parse_int(row.get("score"), 0),
                "duration": duration if duration is not None else 0,
            }
            sessions.append(session)
    return sessions


def main():
    # Import here so this script can run from data/ easily.
    import os
    import sys

    project_root = ROOT.parent
    sys.path.insert(0, str(project_root))
    # Standalone benchmark should not trigger server-startup CSV ingest (ARCADE_INGEST_*).
    for _k in (
        "ARCADE_INGEST_SYNTHETIC_CSV",
        "ARCADE_INGEST_CSV_DIR",
        "ARCADE_INGEST_MAX_PLAYERS",
        "ARCADE_INGEST_MAX_SESSIONS",
        "ARCADE_INGEST_MAX_CHAT",
    ):
        os.environ.pop(_k, None)

    from platform_server.server import PlatformServer

    print("Loading CSVs...")
    game_map = load_game_map()
    players_by_id = load_players()
    sessions = load_sessions()
    print(f"Loaded players: {len(players_by_id)}")
    print(f"Loaded sessions: {len(sessions)}")
    print(f"Loaded games: {len(game_map)}")

    cap = _env_positive_int("ARCADE_BENCHMARK_MAX_SESSIONS")
    if cap is not None and cap < len(sessions):
        sessions = sessions[:cap]
        print(f"Capped sessions to {cap} (ARCADE_BENCHMARK_MAX_SESSIONS)")

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
    total_queries = _env_positive_int("ARCADE_BENCHMARK_MAX_QUERIES", 100000)
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
