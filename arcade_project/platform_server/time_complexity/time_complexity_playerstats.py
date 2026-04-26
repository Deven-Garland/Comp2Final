import time
import random
import matplotlib.pyplot as plt

from platform_server.player_stats import PlayerStats


def build_player_stats(n):
    stats = PlayerStats("test_user")

    for i in range(n):
        game_name = f"game{i}"
        hours = random.uniform(0.5, 3.0)

        stats.log_session(game_name, hours)

    return stats


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


sizes = [100, 500, 1000, 2000, 5000, 10000]

log_chat_times = []
log_session_times = []
most_played_times = []

for n in sizes:
    stats = build_player_stats(n)

    log_chat_time = get_average_time(
        lambda: stats.log_chat(),
        10000
    )

    log_session_time = get_average_time(
        lambda: stats.log_session(f"new_game_{random.randint(1, 1000000)}", 1.5),
        1000
    )

    most_played_time = get_average_time(
        lambda: stats.most_played(),
        50
    )

    log_chat_times.append(log_chat_time)
    log_session_times.append(log_session_time)
    most_played_times.append(most_played_time)

    print("n =", n)
    print("log_chat():", log_chat_time)
    print("log_session():", log_session_time)
    print("most_played():", most_played_time)
    print()


plt.plot(sizes, log_chat_times, marker="o", label="log_chat()")
plt.plot(sizes, log_session_times, marker="o", label="log_session()")
plt.plot(sizes, most_played_times, marker="o", label="most_played()")

plt.xlabel("Number of Unique Games")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of PlayerStats")
plt.legend()
plt.grid(True)
plt.show()
