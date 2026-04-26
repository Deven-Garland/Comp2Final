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

from chat import Chat, GeminiFilter

GeminiFilter.is_clean = lambda self, text: True


def get_average_time(function, trials):
    start = time.perf_counter()

    for _ in range(trials):
        function()

    end = time.perf_counter()

    return (end - start) / trials


def build_chat_sessions(n):
    chat = Chat(buffer_size=20)

    for i in range(n):
        game_id = f"game{i}"
        chat.start_session(game_id)

    return chat


def build_chat_with_messages(n):
    chat = Chat(buffer_size=n)
    game_id = "game1"
    chat.start_session(game_id)

    for i in range(n):
        chat.send_message(game_id, "player1", f"hello message {i}")

    return chat, game_id


sizes = [100, 500, 1000, 2000, 5000, 10000]
trials = 1000

start_session_times = []
send_message_times = []
get_messages_times = []
get_recent_messages_times = []
active_sessions_times = []

for n in sizes:
    chat_sessions = build_chat_sessions(n)

    start_session_time = get_average_time(
        lambda: chat_sessions.start_session(f"new_game_{n}_{random.randint(1, 1000000)}"),
        trials
    )

    send_message_time = get_average_time(
        lambda: chat_sessions.send_message(
            random.choice([f"game{i}" for i in range(n)]),
            "player1",
            "hello"
        ),
        trials
    )

    active_sessions_time = get_average_time(
        lambda: chat_sessions.active_sessions(),
        100
    )

    chat_messages, game_id = build_chat_with_messages(n)

    get_messages_time = get_average_time(
        lambda: chat_messages.get_messages(game_id),
        100
    )

    get_recent_messages_time = get_average_time(
        lambda: chat_messages.get_recent_messages(game_id, 10),
        100
    )

    start_session_times.append(start_session_time)
    send_message_times.append(send_message_time)
    active_sessions_times.append(active_sessions_time)
    get_messages_times.append(get_messages_time)
    get_recent_messages_times.append(get_recent_messages_time)

    print("n =", n)
    print("start_session():", start_session_time)
    print("send_message():", send_message_time)
    print("active_sessions():", active_sessions_time)
    print("get_messages():", get_messages_time)
    print("get_recent_messages():", get_recent_messages_time)
    print()


plt.plot(sizes, start_session_times, marker="o", label="start_session()")
plt.plot(sizes, send_message_times, marker="o", label="send_message()")
plt.plot(sizes, active_sessions_times, marker="o", label="active_sessions()")

plt.xlabel("Number of Active Chat Sessions")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Chat Sessions")
plt.legend()
plt.grid(True)
plt.show()


plt.plot(sizes, get_messages_times, marker="o", label="get_messages()")
plt.plot(sizes, get_recent_messages_times, marker="o", label="get_recent_messages(10)")

plt.xlabel("Number of Messages in One Session")
plt.ylabel("Average Runtime in Seconds")
plt.title("Time Complexity of Chat Message Retrieval")
plt.legend()
plt.grid(True)
plt.show()
