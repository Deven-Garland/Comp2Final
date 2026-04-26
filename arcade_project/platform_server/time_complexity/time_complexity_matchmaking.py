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

from matchmaking import Matchmaking


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


def build_matchmaking(n):
    matchmaking = Matchmaking()

    for i in range(n):
        username = f"user{i}"
        matchmaking.join_queue(username)

    return matchmaking


sizes = [100, 500, 1000, 2000, 5000, 10000]
trials = 1000

join_queue_times = []
match_players_times = []
size_times = []

for n in sizes:
    matchmaking = build_matchmaking(n)

    join_queue_time = get_average_time(
        lambda: matchmaking.join_queue(f"new_user_{n}_{random.randint(1, 1000000)}"),
        trials
    )

    # Build a separate queue for matching so we do not run out of players
    matchmaking_for_matches = build_matchmaking(n + trials * 2)

    match_players_time = get_average_time(
        lambda: matchmaking_for_matches.match_players(2),
        trials
    )

    size_time = get_average_time(
        lambda: matchmaking.size(),
        trials
    )

    join_queue_times.append(join_queue_time)
    match_players_times.append(match_players_time)
    size_times.append(size_time)

    print("n =", n)
    print("join_queue():", join_queue_time)
    print("match_players(2):", match_players_time)
    print("size():", size_time)
    print()


plt.plot(sizes, join_queue_times, marker="o", label="join_queue()")
plt.plot(sizes, match_players_times, marker="o", label="match_players(2)")
plt.plot(sizes, size_times, marker="o", label="size()")

plt.xlabel("Number of Players in Queue")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Matchmaking")
plt.legend()
plt.grid(True)
plt.show()
