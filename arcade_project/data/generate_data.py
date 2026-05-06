import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


# --------------------------
# SETTINGS
# --------------------------
NUM_PLAYERS = 10000
NUM_SESSIONS = 100000
NUM_CHATS = 50000
RANDOM_SEED = 3822

DATASET_DIR = Path(__file__).resolve().parent / "synthetic_dataset"
PLAYER_FILE = DATASET_DIR / "players.csv"
SESSION_FILE = DATASET_DIR / "sessions.csv"
CHAT_FILE = DATASET_DIR / "chat.csv"
GAME_FILE = DATASET_DIR / "games.csv"

TEAM_GAMES = [
    (1, "mennah", "Team Mennah", "survival"),
    (2, "deven", "Team Deven", "platformer"),
    (3, "ellie", "Team Ellie", "strategy"),
    (4, "vraj", "Team Vraj", "arena"),
    (5, "kimberly", "Team Kimberly", "adventure"),
]

COUNTRIES = [
    "US",
    "CA",
    "MX",
    "BR",
    "GB",
    "DE",
    "IN",
    "JP",
    "KR",
    "AU",
]

CHAT_MESSAGES = [
    "gg",
    "nice play",
    "that was close",
    "lag spike",
    "need backup",
    "omw",
    "bruh",
    "good round",
    "where are you",
    "clutch",
]


def _random_datetime_within_last_year():
    now = datetime.now(timezone.utc)
    delta_seconds = random.randint(0, 365 * 24 * 60 * 60)
    return now - timedelta(seconds=delta_seconds)


def _format_timestamp_messy(ts):
    formats = [
        ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        ts.strftime("%Y-%m-%d %H:%M:%S"),
        ts.strftime("%m/%d/%Y %I:%M:%S %p"),
        ts.strftime("%Y/%m/%d %H:%M"),
        str(int(ts.timestamp())),
    ]
    return random.choice(formats)


def _name_variation(name):
    options = [
        name.lower(),
        name.upper(),
        name.replace("_", ""),
        name + "_1",
        name + "x",
        name + ".",
        name.replace("player", "plyr"),
    ]
    return random.choice(options)


def generate_players():
    rows = [["player_id", "username", "display_name", "country", "level", "created_at"]]

    for player_id in range(1, NUM_PLAYERS + 1):
        username = f"player{player_id:05d}"
        display_name = f"Player {player_id}"
        country = random.choice(COUNTRIES)
        level = random.randint(1, 100)
        created_at = _format_timestamp_messy(_random_datetime_within_last_year())

        r = random.random()
        if r < 0.04:
            display_name = ""  # missing display name
        elif r < 0.08:
            country = ""  # missing country
        elif r < 0.11 and player_id > 1:
            # duplicate-ish username with slight variation
            source_id = random.randint(1, player_id - 1)
            username = _name_variation(f"player{source_id:05d}")
            display_name = _name_variation(f"Player_{source_id}")

        rows.append([player_id, username, display_name, country, level, created_at])

    with PLAYER_FILE.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def generate_sessions():
    rows = [["session_id", "player_id", "game_id", "start_time", "end_time", "score"]]

    game_ids = [game_id for game_id, _, _, _ in TEAM_GAMES]
    for session_id in range(1, NUM_SESSIONS + 1):
        player_id = random.randint(1, NUM_PLAYERS)
        game_id = random.choice(game_ids)
        start_time = _random_datetime_within_last_year()
        duration_seconds = random.randint(60, 2 * 60 * 60)
        end_time = start_time + timedelta(seconds=duration_seconds)
        score = random.randint(0, 5000)

        score_roll = random.random()
        if score_roll < 0.04:
            score = ""  # null-ish score
        elif score_roll < 0.07:
            score = "null"
        elif score_roll < 0.11:
            score = -score  # negative score

        end_time_value = _format_timestamp_messy(end_time)
        if random.random() < 0.06:
            end_time_value = ""  # missing end time

        rows.append(
            [
                session_id,
                player_id,
                game_id,
                _format_timestamp_messy(start_time),
                end_time_value,
                score,
            ]
        )

    with SESSION_FILE.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def generate_chat():
    rows = [["chat_id", "session_id", "player_id", "game_id", "message", "sent_at"]]

    for chat_id in range(1, NUM_CHATS + 1):
        session_id = random.randint(1, NUM_SESSIONS)
        player_id = random.randint(1, NUM_PLAYERS)
        game_id = random.choice([game[0] for game in TEAM_GAMES])
        message = random.choice(CHAT_MESSAGES)
        sent_at = _format_timestamp_messy(_random_datetime_within_last_year())

        if random.random() < 0.03:
            message = ""  # missing message text
        if random.random() < 0.02:
            sent_at = ""  # missing timestamp

        rows.append([chat_id, session_id, player_id, game_id, message, sent_at])

    with CHAT_FILE.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def generate_games():
    rows = [["game_id", "game_name", "team", "genre"]]
    for game_id, game_name, team, genre in TEAM_GAMES:
        rows.append([game_id, game_name, team, genre])

    with GAME_FILE.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


if __name__ == "__main__":
    random.seed(RANDOM_SEED)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic dataset...")
    generate_players()
    print("players.csv done")
    generate_sessions()
    print("sessions.csv done")
    generate_chat()
    print("chat.csv done")
    generate_games()
    print("games.csv done")
    print("All dataset files generated.")
