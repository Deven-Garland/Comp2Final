import os
import sys
import time
import random
import matplotlib.pyplot as plt



current_folder = os.path.dirname(os.path.abspath(__file__))

platform_server_folder = os.path.dirname(current_folder)


project_folder = os.path.dirname(platform_server_folder)

game_folder = os.path.join(project_folder, "code", "game")


sys.path.insert(0, platform_server_folder)
sys.path.insert(0, game_folder)

from accounts import Accounts
# Turn off file loading/saving so we only measure the data structures
Accounts._load = lambda self: None
Accounts._save = lambda self: None


def build_accounts(n):
    accounts = Accounts()

    for i in range(n):
        username = f"user{i}"
        accounts.register(username, "password123")

    return accounts


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


sizes = [100, 500, 1000, 2000, 5000, 10000]
trials = 1000

register_times = []
login_times = []
exists_times = []
get_account_times = []

for n in sizes:
    account = build_account(n)
    usernames = [f"user{i}" for i in range(n)]

    register_time = get_average_time(
        lambda: accounts.register(f"new_user_{n}_{random.randint(1, 1000000)}", "password123"),
        trials
    )

    login_time = get_average_time(
        lambda: accounts.login(random.choice(usernames), "password123"),
        trials
    )

    exists_time = get_average_time(
        lambda: accounts.exists(random.choice(usernames)),
        trials
    )

    get_account_time = get_average_time(
        lambda: account.get_account(random.choice(usernames)),
        trials
    )

    register_times.append(register_time)
    login_times.append(login_time)
    exists_times.append(exists_time)
    get_account_times.append(get_account_time)

    print("n =", n)
    print("register():", register_time)
    print("login():", login_time)
    print("exists():", exists_time)
    print("get_account():", get_account_time)
    print()


plt.plot(sizes, register_times, marker="o", label="register()")
plt.plot(sizes, login_times, marker="o", label="login()")
plt.plot(sizes, exists_times, marker="o", label="exists()")
plt.plot(sizes, get_account_times, marker="o", label="get_account()")

plt.xlabel("Number of Accounts")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Accounts")
plt.legend()
plt.grid(True)
plt.show()
