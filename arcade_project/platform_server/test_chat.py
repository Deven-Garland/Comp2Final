from platform_server.chat import Chat

c = Chat()

print(c.send_message("game1", "alice", "I killed you haha"))   # True
print(c.send_message("game1", "alice", "what the fuck"))       # False
print(c.send_message("game1", "alice", "good game everyone"))  # True

for msg in c.get_messages("game1"):
    print(msg)