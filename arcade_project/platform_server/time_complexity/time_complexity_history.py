import time
import matplotlib.pyplot as plt

import os
import sys
import time
import random
import matplotlib.pyplot as plt


current_folder = os.path.dirname(os.path.abspath(__file__))


platform_server_folder = os.path.dirname(current_folder)


project_folder = os.path.dirname(platform_server_folder)


sys.path.insert(0, project_folder)


sys.path.insert(0, platform_server_folder)

from history import History


def build_history(n):
    history = History()

    for i in range(n):
        game_id = f"game{i}"
        players = ["player1", "player2"]
        winner = "player1"

        history.add_match(game_id, players, winner)

    return history


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


sizes = [100, 500, 1000, 2000, 5000, 10000]
trials = 1000

add_match_times = []
get_history_times = []
iterate_history_times = []

for n in sizes:
    history = build_history(n)

    add_match_time = get_average_time(
        lambda: history.add_match("new_game", ["player1", "player2"], "player1"),
        trials
    )

    get_history_time = get_average_time(
        lambda: history.get_player_history("player1"),
        trials
    )

    iterate_history_time = get_average_time(
        lambda: [match for match in history.get_player_history("player1")],
        trials
    )

    add_match_times.append(add_match_time)
    get_history_times.append(get_history_time)
    iterate_history_times.append(iterate_history_time)

    print("n =", n)
    print("add_match():", add_match_time)
    print("get_player_history():", get_history_time)
    print("iterate history:", iterate_history_time)
    print()


plt.plot(sizes, add_match_times, marker="o", label="add_match()")
plt.plot(sizes, get_history_times, marker="o", label="get_player_history()")
plt.plot(sizes, iterate_history_times, marker="o", label="iterate history")

plt.xlabel("Number of Matches")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Match History")
plt.legend()
plt.grid(True)
plt.show()
