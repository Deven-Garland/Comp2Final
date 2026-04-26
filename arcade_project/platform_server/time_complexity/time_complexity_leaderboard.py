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


from leaderboard import Leaderboard


def build_leaderboard(n):
    leaderboard = Leaderboard()

    for i in range(n):
        username = f"user{i}"
        score = random.randint(1, 100000)

        leaderboard.add_score(username, score)

    return leaderboard


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


sizes = [100, 500, 1000, 2000, 5000, 10000]
trials = 100

add_score_times = []
update_score_times = []
top_k_times = []
range_query_times = []

for n in sizes:
    leaderboard = build_leaderboard(n)
    usernames = [f"user{i}" for i in range(n)]

    add_score_time = get_average_time(
        lambda: leaderboard.add_score(f"new_user_{n}_{random.randint(1, 1000000)}", random.randint(1, 100000)),
        trials
    )

    update_score_time = get_average_time(
        lambda: leaderboard.add_score(random.choice(usernames), random.randint(1, 100000)),
        trials
    )

    top_k_time = get_average_time(
        lambda: leaderboard.top_k(10),
        trials
    )

    range_query_time = get_average_time(
        lambda: leaderboard.range_query(25000, 75000),
        trials
    )

    add_score_times.append(add_score_time)
    update_score_times.append(update_score_time)
    top_k_times.append(top_k_time)
    range_query_times.append(range_query_time)

    print("n =", n)
    print("add_score new player:", add_score_time)
    print("add_score existing player:", update_score_time)
    print("top_k(10):", top_k_time)
    print("range_query():", range_query_time)
    print()


plt.plot(sizes, add_score_times, marker="o", label="add_score new player")
plt.plot(sizes, update_score_times, marker="o", label="add_score existing player")
plt.plot(sizes, top_k_times, marker="o", label="top_k(10)")
plt.plot(sizes, range_query_times, marker="o", label="range_query()")

plt.xlabel("Number of Leaderboard Entries")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Leaderboard")
plt.legend()
plt.grid(True)
plt.show()
