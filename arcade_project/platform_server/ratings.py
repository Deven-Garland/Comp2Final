from datastructures.hash_table import HashTable
from datastructures.array import ArrayList
from datastructures.heap import MinHeap, MaxHeap
 
 
class GameRating:
    """Holds the anonymous star scores for one game."""
    def __init__(self, game_name):
        self.game_name = game_name
        self.scores = ArrayList()
 
    def add_score(self, stars):
        self.scores.append(stars)
 
    def average(self):
        if len(self.scores) == 0:
            return 0
        total = 0
        for s in self.scores:
            total += s
        return round(total / len(self.scores), 2)
 
 
class Ratings:
    def __init__(self, game_names):
        # HashTable: platform game id (C++ server key) -> GameRating. O(1) lookup.
        self.game_ratings = HashTable()
        for game_name in game_names:
            self.game_ratings[game_name] = GameRating(game_name)
 
    def rate(self, game_name, stars):
        """Player selects 1-5 stars for a game."""
        if stars < 1 or stars > 5:
            raise ValueError("Please select between 1 and 5 stars")
        if game_name not in self.game_ratings:
            # Keep ratings usable even if game registry changed across deployments.
            self.game_ratings[game_name] = GameRating(game_name)
        self.game_ratings[game_name].add_score(stars)
 
    def get_rankings(self):
        """Return all games from highest to lowest rated."""
        heap = MaxHeap()
        for game_name in self.game_ratings:
            gr = self.game_ratings[game_name]
            heap.insert((gr.average(), game_name))
 
        ranked = ArrayList()
        while not heap.is_empty():
            avg, name = heap.remove_max()
            ranked.append({"game": name, "avg_rating": avg})
        return tuple(ranked)
 
    def get_highest_rated(self):
        """Return the single highest rated game."""
        heap = MaxHeap()
        for game_name in self.game_ratings:
            gr = self.game_ratings[game_name]
            heap.insert((gr.average(), game_name))
        if heap.is_empty():
            return None
        avg, name = heap.get_max()
        return {"game": name, "avg_rating": avg}
 
    def get_lowest_rated(self):
        """Return the single lowest rated game."""
        heap = MinHeap()
        for game_name in self.game_ratings:
            gr = self.game_ratings[game_name]
            heap.insert((gr.average(), game_name))
        if heap.is_empty():
            return None
        avg, name = heap.get_min()
        return {"game": name, "avg_rating": avg}