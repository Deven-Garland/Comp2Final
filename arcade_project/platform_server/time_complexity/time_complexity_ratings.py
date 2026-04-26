import time
import random
import matplotlib.pyplot as plt

from platform_server.ratings import Ratings


def build_ratings(n, ratings_per_game):
    game_names = []

    for i in range(n):
        game_names.append(f"game{i}")

    ratings = Ratings(game_names)

    for game in game_names:
        for _ in range(ratings_per_game):
            stars = random.randint(1, 5)
            ratings.rate(game, stars)

    return ratings, game_names


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


sizes = [10, 50, 100, 250, 500, 1000]
ratings_per_game = 10

rate_times = []
rankings_times = []
highest_times = []
lowest_times = []

for n in sizes:
    ratings, game_names = build_ratings(n, ratings_per_game)

    rate_time = get_average_time(
        lambda: ratings.rate(random.choice(game_names), random.randint(1, 5)),
        1000
    )

    rankings_time = get_average_time(
        lambda: ratings.get_rankings(),
        50
    )

    highest_time = get_average_time(
        lambda: ratings.get_highest_rated(),
        50
    )

    lowest_time = get_average_time(
        lambda: ratings.get_lowest_rated(),
        50
    )

    rate_times.append(rate_time)
    rankings_times.append(rankings_time)
    highest_times.append(highest_time)
    lowest_times.append(lowest_time)

    print("n =", n)
    print("rate():", rate_time)
    print("get_rankings():", rankings_time)
    print("get_highest_rated():", highest_time)
    print("get_lowest_rated():", lowest_time)
    print()


plt.plot(sizes, rate_times, marker="o", label="rate()")
plt.plot(sizes, rankings_times, marker="o", label="get_rankings()")
plt.plot(sizes, highest_times, marker="o", label="get_highest_rated()")
plt.plot(sizes, lowest_times, marker="o", label="get_lowest_rated()")

plt.xlabel("Number of Games")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Ratings")
plt.legend()
plt.grid(True)
plt.show()
