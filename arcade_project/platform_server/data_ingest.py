"""
data_ingest.py - Seed demo accounts and optionally load synthetic CSVs.

Offline project test (no TCP server — in-memory PlatformServer only):

  cd arcade_project
  python platform_server/data_ingest.py

That runs the CSV load + query simulation in data/benchmark_platform_from_csv.py.

Default (no env): registers three demo users — CSVs are NOT read.

To load arcade_project/data/synthetic_dataset into the live TCP platform server:

  PowerShell:
    $env:ARCADE_INGEST_SYNTHETIC_CSV="1"
    python platform_runner.py

Optional:
  ARCADE_INGEST_CSV_DIR        Path to folder containing players/sessions/games CSVs
  ARCADE_SYNTHETIC_PASSWORD    Password for newly registered CSV users (default: synthetic)
  ARCADE_INGEST_MAX_PLAYERS    Stop after reading this many player rows (optional)
  ARCADE_INGEST_MAX_SESSIONS   Stop after processing this many session rows (optional)
  ARCADE_INGEST_MAX_CHAT       Ingest up to N chat rows; 0 = skip chat entirely (default 0)

Column expectations match arcade_project/data/benchmark_platform_from_csv.py.
"""

from __future__ import annotations

import csv
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# Running as `python platform_server/data_ingest.py` needs arcade_project on sys.path.
if __package__ in (None, ""):
    _AP_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(_AP_ROOT))

from datastructures.array import ArrayList
from datastructures.hash_table import HashTable

if TYPE_CHECKING:
    from platform_server.server import PlatformServer


def _arcade_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_synthetic_dataset_dir() -> Path:
    return _arcade_project_root() / "data" / "synthetic_dataset"


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
    formats = ArrayList()
    formats.append("%Y-%m-%dT%H:%M:%SZ")
    formats.append("%Y-%m-%d %H:%M:%S")
    formats.append("%m/%d/%Y %I:%M:%S %p")
    formats.append("%d/%m/%Y %I:%M:%S %p")
    formats.append("%m/%d/%Y %I:%M %p")
    formats.append("%Y/%m/%d %H:%M")
    formats.append("%Y-%m-%d %H:%M")
    formats.append("%d/%m/%Y %H:%M:%S")
    fi = 0
    while fi < len(formats):
        fmt = formats[fi]
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            fi += 1
            continue
    return None


def canonical_username(value: str) -> str:
    name = (value or "").strip().lower()
    if not name:
        return ""
    return "".join(ch for ch in name if ch.isalnum())


def _env_int(name: str, default: Optional[int]) -> Optional[int]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        v = int(raw)
        return v if v >= 0 else default
    except ValueError:
        return default


@contextmanager
def suspend_persistence(platform: "PlatformServer"):
    """Avoid writing JSON on every row during bulk ingest."""
    original_runtime_save = platform._save_runtime_state
    original_accounts_save = platform.accounts._save

    platform._save_runtime_state = lambda: None
    platform.accounts._save = lambda: None
    try:
        yield
    finally:
        platform._save_runtime_state = original_runtime_save
        platform.accounts._save = original_accounts_save
        platform.accounts._save()
        platform._save_runtime_state()


class DataIngest:
    def __init__(self, accounts, leaderboard, catalog):
        self.accounts = accounts
        self.leaderboard = leaderboard
        self.catalog = catalog

    def load_data(self, platform: Optional["PlatformServer"] = None) -> None:
        flag = os.environ.get("ARCADE_INGEST_SYNTHETIC_CSV", "").strip().lower()
        truthy = HashTable()
        truthy["1"] = True
        truthy["true"] = True
        truthy["yes"] = True
        if flag in truthy:
            if platform is None:
                raise RuntimeError(
                    "ARCADE_INGEST_SYNTHETIC_CSV is set — call load_data(platform=self) "
                    "from PlatformServer.__init__ after full construction."
                )
            self._ingest_synthetic_csv(platform)
            return

        users = ArrayList()
        d1 = HashTable()
        d1["username"] = "deven"
        d1["password"] = "67"
        d1["score"] = 1500
        users.append(d1)
        d2 = HashTable()
        d2["username"] = "ellie"
        d2["password"] = "cute"
        d2["score"] = 1200
        users.append(d2)
        d3 = HashTable()
        d3["username"] = "vraj"
        d3["password"] = "yo"
        d3["score"] = 1800
        users.append(d3)

        ui = 0
        while ui < len(users):
            row = users[ui]
            username = row["username"]
            password = row["password"]
            score = row["score"]
            self.accounts.register(username, password)
            self.leaderboard.add_score(username, score)
            meta = HashTable()
            meta["score"] = score
            self.catalog.add_player(username, meta)
            ui += 1

    # --- Synthetic CSV -----------------------------------------------------

    def _load_game_map(self, games_csv: Path) -> HashTable:
        game_map = HashTable()
        with games_csv.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                game_id = parse_int(row.get("game_id"))
                if game_id is None:
                    continue
                name = (row.get("game_name") or "").strip()
                if name:
                    game_map[game_id] = name
        return game_map

    def _load_players_by_id(self, players_csv: Path, max_rows: Optional[int]) -> HashTable:
        """player_id -> canonical username (later rows overwrite same id)."""
        players = HashTable()
        seen = 0
        with players_csv.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if max_rows is not None and seen >= max_rows:
                    break
                seen += 1
                username = canonical_username(row.get("username", ""))
                if not username:
                    continue
                player_id = parse_int(row.get("player_id"))
                if player_id is None:
                    continue
                players[player_id] = username
        return players

    def _ingest_synthetic_csv(self, platform: "PlatformServer") -> None:
        root = Path(os.environ.get("ARCADE_INGEST_CSV_DIR", str(default_synthetic_dataset_dir()))).expanduser()
        players_csv = root / "players.csv"
        sessions_csv = root / "sessions.csv"
        games_csv = root / "games.csv"
        chat_csv = root / "chat.csv"

        required_csvs = ArrayList()
        required_csvs.append(players_csv)
        required_csvs.append(sessions_csv)
        required_csvs.append(games_csv)
        ri = 0
        while ri < len(required_csvs):
            path = required_csvs[ri]
            ri += 1
            if not path.is_file():
                print(f"[data_ingest] Missing CSV: {path}")
                print("[data_ingest] Generate data (arcade_project/data/generate_data.py) or set ARCADE_INGEST_CSV_DIR.")
                return

        max_rows_players = _env_int("ARCADE_INGEST_MAX_PLAYERS", None)
        max_sessions = _env_int("ARCADE_INGEST_MAX_SESSIONS", None)
        max_chat = _env_int("ARCADE_INGEST_MAX_CHAT", 0)
        password = os.environ.get("ARCADE_SYNTHETIC_PASSWORD", "synthetic").strip() or "synthetic"

        game_map = self._load_game_map(games_csv)
        players_by_id = self._load_players_by_id(players_csv, max_rows_players)

        print(f"[data_ingest] Ingesting synthetic CSVs from {root}")
        print(f"[data_ingest] Player index size (by id): {len(players_by_id)} | games mapped: {len(game_map)}")

        uniq = HashTable()
        usernames = ArrayList()
        for pid in players_by_id:
            u = players_by_id.get(pid)
            if not u:
                continue
            if u not in uniq:
                uniq[u] = True
                usernames.append(u)

        registered = 0
        with suspend_persistence(platform):
            for i in range(len(usernames)):
                username = usernames[i]
                if not self.accounts.exists(username):
                    if self.accounts.register(username, password):
                        registered += 1
                catalog_meta = HashTable()
                catalog_meta["ingested"] = True
                self.catalog.add_player(username, catalog_meta)

            sessions_done = 0
            with sessions_csv.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if max_sessions is not None and sessions_done >= max_sessions:
                        break
                    player_id = parse_int(row.get("player_id"))
                    game_id = parse_int(row.get("game_id"))
                    if player_id is None or game_id is None:
                        continue
                    username = players_by_id.get(player_id)
                    if not username or not platform.accounts.exists(username):
                        continue

                    game_name = game_map.get(game_id) if game_id in game_map else "global"

                    start_dt = parse_timestamp(row.get("start_time"))
                    end_dt = parse_timestamp(row.get("end_time"))
                    if start_dt and end_dt:
                        duration = max(0, int((end_dt - start_dt).total_seconds()))
                        ended_ts = end_dt.timestamp()
                    else:
                        duration = max(0, parse_int(row.get("duration"), 0) or 0)
                        if end_dt:
                            ended_ts = end_dt.timestamp()
                        elif start_dt:
                            ended_ts = start_dt.timestamp()
                        else:
                            ended_ts = 0.0

                    score = parse_int(row.get("score"), 0) or 0
                    session_id = parse_int(row.get("session_id"), sessions_done)

                    roster = ArrayList()
                    roster.append(username)
                    platform.history.add_match(
                        session_id,
                        roster,
                        username,
                        score=max(0, score),
                        duration=duration,
                        ended_at=ended_ts,
                        game_name=game_name,
                    )
                    platform.record_session_result(
                        game=game_name,
                        username=username,
                        score=max(0, score),
                        play_time=max(0, duration),
                    )
                    sessions_done += 1

            if max_chat and chat_csv.is_file():
                chat_n = 0
                with chat_csv.open("r", newline="", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if chat_n >= max_chat:
                            break
                        message = (row.get("message") or "").strip()
                        if not message:
                            continue
                        player_id = parse_int(row.get("player_id"))
                        session_id_c = parse_int(row.get("session_id"), 0)
                        if player_id is None:
                            continue
                        sender = players_by_id.get(player_id)
                        if not sender or not platform.accounts.exists(sender):
                            continue
                        channel = f"synthetic_sess:{session_id_c}"
                        platform.chat.start_session(channel)
                        gid = parse_int(row.get("game_id"))
                        gname = game_map.get(gid, "global") if gid is not None else "global"
                        if gname is None:
                            gname = "global"
                        platform.send_message(channel, sender, message, game=gname)
                        chat_n += 1
                print(f"[data_ingest] Chat rows attempted: {chat_n} (moderation may drop some)")
            elif max_chat > 0 and not chat_csv.is_file():
                print(f"[data_ingest] ARCADE_INGEST_MAX_CHAT={max_chat} but no chat.csv at {chat_csv}")

        print(f"[data_ingest] Registered ~{registered} new accounts; replayed ~{sessions_done} sessions.")


def run_standalone_synthetic_benchmark() -> None:
    """
    Load synthetic_dataset CSVs into an in-memory PlatformServer, replay sessions,
    then run the timed leaderboard/history-style query batch. No socket server.
    Delegates to arcade_project/data/benchmark_platform_from_csv.py.
    """
    import importlib.util
    import sys

    root = _arcade_project_root()
    sys.path.insert(0, str(root))

    keys = ArrayList()
    keys.append("ARCADE_INGEST_SYNTHETIC_CSV")
    keys.append("ARCADE_INGEST_CSV_DIR")
    keys.append("ARCADE_INGEST_MAX_PLAYERS")
    keys.append("ARCADE_INGEST_MAX_SESSIONS")
    keys.append("ARCADE_INGEST_MAX_CHAT")

    saved = HashTable()
    i = 0
    while i < len(keys):
        k = keys[i]
        if k in os.environ:
            saved[k] = os.environ[k]
            del os.environ[k]
        i += 1

    try:
        bench_path = root / "data" / "benchmark_platform_from_csv.py"
        if not bench_path.is_file():
            print(f"[data_ingest] Benchmark script not found: {bench_path}")
            return
        spec = importlib.util.spec_from_file_location("_mosfet_csv_benchmark", bench_path)
        if spec is None or spec.loader is None:
            print("[data_ingest] Could not load benchmark module.")
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
    finally:
        for k in saved:
            os.environ[k] = saved[k]


if __name__ == "__main__":
    print("Synthetic dataset offline test (in-memory platform; no TCP).")
    run_standalone_synthetic_benchmark()
