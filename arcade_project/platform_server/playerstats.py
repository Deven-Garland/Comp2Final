from datastructures.hash_table import HashTable
from datastructures.array import ArrayList
from datastructures.heap import MaxHeap
 
 
class PlayerStats:
    def __init__(self, username):
        self.username = username
        self.chats_sent = 0
        self.hours_played = 0.0
 
        # ArrayList: ordered log of every game session played
        self.games_played = ArrayList()
 
        # HashTable: game name -> play count, for fast tallying
        self._play_counts = HashTable()
 
    def log_chat(self):
        self.chats_sent += 1
 
    def log_session(self, game_name, hours):
        self.hours_played += hours
        self.games_played.append(game_name)
 
        # Update play count in HashTable
        if game_name in self._play_counts:
            self._play_counts[game_name] += 1
        else:
            self._play_counts[game_name] = 1
 
    def most_played(self):
        """Return games ranked by play count using a MaxHeap."""
        heap = MaxHeap()
        for game in self._play_counts:
            count = self._play_counts[game]
            heap.insert((count, game))
 
        ranked = ArrayList()
        while not heap.is_empty():
            count, game = heap.remove_max()
            ranked.append((game, count))
        return ranked
 
    def __str__(self):
        return (f"PlayerStats({self.username}: "
                f"{self.chats_sent} chats, "
                f"{self.hours_played}h played)")