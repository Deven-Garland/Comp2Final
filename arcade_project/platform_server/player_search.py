"""
player_search.py - Prefix-based player search index

Author: Ellie Lutz
Date: Spring 2026
Lab: Final Project - Player Search
"""

from datastructures.hash_table import HashTable
from datastructures.array import ArrayList


class PlayerSearch:
    def __init__(self):
        self._profiles = HashTable()
        self._sorted_names = ArrayList()

    def register(self, username, display_name, profile):
        self._profiles[username] = profile
        if not self._contains_name(username):
            self._sorted_insert(username)

    def _contains_name(self, username):
        for i in range(len(self._sorted_names)):
            if self._sorted_names[i] == username:
                return True
        return False

    def _sorted_insert(self, username):
        lo, hi = 0, len(self._sorted_names)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._sorted_names[mid] < username:
                lo = mid + 1
            else:
                hi = mid
        self._sorted_names.insert(lo, username)

    def _bisect_left(self, prefix):
        lo, hi = 0, len(self._sorted_names)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._sorted_names[mid] < prefix:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def search_prefix(self, prefix):
        if not prefix:
            return ArrayList()
        prefix = prefix.lower()
        results = ArrayList()
        i = self._bisect_left(prefix)
        while i < len(self._sorted_names):
            name = self._sorted_names[i]
            if not name.lower().startswith(prefix):
                break
            profile = self._profiles[name]
            if profile is not None:
                results.append(profile)
            i += 1
        return results

    def get_profile(self, username):
        if username not in self._profiles:
            return None
        return self._profiles[username]

    def __len__(self):
        return len(self._sorted_names)