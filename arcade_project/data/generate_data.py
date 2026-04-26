import random
import csv

# --------------------------
# SETTINGS (adjust if needed)
# --------------------------
NUM_PLAYERS = 10000
NUM_SESSIONS = 100000
NUM_CHATS = 50000
NUM_GAMES = 120

PLAYER_FILE = "../data/synthetic_dataset/players.csv"
SESSION_FILE = "../data/synthetic_dataset/sessions.csv"
CHAT_FILE = "../data/synthetic_dataset/chat.csv"
GAME_FILE = "../data/synthetic_dataset/games.csv"


# --------------------------
# PLAYERS
# --------------------------
def generate_players():
    rows = [["player_id", "username", "level"]]

    for i in range(1, NUM_PLAYERS + 1):
        username = f"Player{i}"

        # messy data
        r = random.random()
        if r < 0.03:
            username = ""  # missing
        elif r < 0.06:
            username = f"Player{random.randint(1, NUM_PLAYERS)}"  # duplicate

        level = random.randint(1, 100)

        rows.append([i, username, level])

    with open(PLAYER_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)


# --------------------------
# SESSIONS
# --------------------------
def generate_sessions():
    rows = [["session_id", "player_id", "game_id", "score", "duration"]]

    for i in range(1, NUM_SESSIONS + 1):
        player_id = random.randint(1, NUM_PLAYERS)
        game_id = random.randint(1, NUM_GAMES)

        # messy score
        score = random.randint(0, 1000)
        if random.random() < 0.05:
            score = -score

        # messy duration
        duration = random.randint(10, 500)
        if random.random() < 0.05:
            duration = ""

        rows.append([i, player_id, game_id, score, duration])

    with open(SESSION_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)


# --------------------------
# CHAT MESSAGES (NEW 🔥)
# --------------------------
def generate_chat():
    rows = [["chat_id", "player_id", "game_id", "message"]]

    sample_messages = [
        "gg", "nice", "lol", "wow", "no way", "help", "go go go",
        "that was close", "what happened", "lag", "bruh"
    ]

    for i in range(1, NUM_CHATS + 1):
        player_id = random.randint(1, NUM_PLAYERS)
        game_id = random.randint(1, NUM_GAMES)

        msg = random.choice(sample_messages)

        # messy data
        if random.random() < 0.03:
            msg = ""

        rows.append([i, player_id, game_id, msg])

    with open(CHAT_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)


# --------------------------
# GAMES (FIXED 🔥)
# --------------------------
def generate_games():
    rows = [["game_id", "game_name"]]

    for i in range(1, NUM_GAMES + 1):
        rows.append([i, f"Game_{i}"])

    with open(GAME_FILE, "w", newline="") as f:
        csv.writer(f).writerows(rows)


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    print("Generating dataset...")

    generate_players()
    print("Players done")

    generate_sessions()
    print("Sessions done")

    generate_chat()
    print("Chat done")

    generate_games()
    print("Games done")

    print("All data generated successfully")
