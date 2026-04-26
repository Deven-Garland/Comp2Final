import random
import csv

# SETTINGS
NUM_PLAYERS = 10000
NUM_SESSIONS = 100000

PLAYER_FILE = "../data/synthetic_dataset/players.csv"
SESSION_FILE = "../data/synthetic_dataset/sessions.csv"
GAME_FILE = "../data/synthetic_dataset/games.csv"

# Match the actual 5 games in your arcade.
GAME_IDS = [1, 2, 3, 4, 5]


# --------------------------
# Generate Players
# --------------------------
def generate_players():
    with open(PLAYER_FILE, "w", newline="") as f:
        writer = csv.writer(f)

        # header
        writer.writerow(["player_id", "username", "level"])

        for i in range(1, NUM_PLAYERS + 1):
            username = f"Player{i}"

            # make some messy data
            if random.random() < 0.05:
                username = ""  # missing name
            elif random.random() < 0.05:
                username = f"Player{random.randint(1, NUM_PLAYERS)}"  # duplicate

            level = random.randint(1, 100)

            writer.writerow([i, username, level])


# --------------------------
# Generate Sessions
# --------------------------
def generate_sessions():
    with open(SESSION_FILE, "w", newline="") as f:
        writer = csv.writer(f)

        # header
        writer.writerow(["session_id", "player_id", "game_id", "score", "duration"])

        for i in range(1, NUM_SESSIONS + 1):
            player_id = random.randint(1, NUM_PLAYERS)
            game_id = random.choice(GAME_IDS)

            # messy scores
            if random.random() < 0.05:
                score = -random.randint(0, 100)  # invalid
            else:
                score = random.randint(0, 1000)

            # messy duration
            if random.random() < 0.05:
                duration = None  # missing
            else:
                duration = random.randint(10, 500)

            writer.writerow([i, player_id, game_id, score, duration])


# --------------------------
# Generate Games
# --------------------------
def generate_games():
    with open(GAME_FILE, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["game_id", "game_name"])

        writer.writerow([1, "mennah"])
        writer.writerow([2, "deven"])
        writer.writerow([3, "ellie"])
        writer.writerow([4, "vraj"])
        writer.writerow([5, "kimberly"])


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    print("Generating data...")

    generate_players()
    generate_sessions()
    generate_games()

    print("Done.")
