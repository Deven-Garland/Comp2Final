"""
player_search.py - Lightweight player directory + prefix search

Keeps a simple in-memory index for username lookup and profile retrieval.
"""

from datastructures.hash_table import HashTable


class PlayerSearch:
    def __init__(self):
        # username -> {"username": str, "display_name": str, "profile": dict}
        self._players = HashTable()

    def register(self, username, display_name, profile):
        """
        Add or update a player record in the search index.
        """
        self._players[username] = {
            "username": username,
            "display_name": display_name,
            "profile": profile or {},
        }

    def search_prefix(self, prefix):
        """
        Return players whose usernames start with prefix (case-insensitive).
        """
        if prefix is None:
            prefix = ""
        prefix_lower = str(prefix).lower()
        matches = []
        for username in self._players:
            if str(username).lower().startswith(prefix_lower):
                entry = self._players[username]
                matches.append(
                    {
                        "username": entry["username"],
                        "display_name": entry["display_name"],
                    }
                )
        matches.sort(key=lambda item: item["username"].lower())
        return matches

    def get_profile(self, username):
        """
        Return the stored profile dictionary for a username.
        """
        if username not in self._players:
            return None
        return self._players[username]["profile"]
