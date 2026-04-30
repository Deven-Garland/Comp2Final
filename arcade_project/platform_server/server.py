# ============================================================
# server.py PATCH — ratings persistence
# Replace these two methods in PlatformServer in server.py
# ============================================================

    def _save_runtime_state(self):
        payload = HashTable()
        payload["next_game_id"] = self.next_game_id
        payload["active_game_id"] = self.active_game_id
        payload["instance_player_counts"] = self.instance_player_counts
        payload["game_counters"] = self._serialize_game_counters()
        payload["history"] = self._serialize_history()
        # Persist ratings so they survive server restarts
        payload["ratings"] = self._serialize_ratings()
        try:
            with open(RUNTIME_STATE_FILE, "w", encoding="utf-8") as file:
                json.dump(_to_builtin_json(payload), file, indent=2)
        except Exception as error:
            print(f"[platform] Could not save runtime state: {error}")

    def _serialize_ratings(self):
        """Convert ratings to a plain dict: {game_name: [score, score, ...]}"""
        data = HashTable()
        for game_name in self.ratings.game_ratings:
            gr = self.ratings.game_ratings[game_name]
            scores = ArrayList()
            for s in gr.scores:
                scores.append(s)
            data[game_name] = scores
        return data

    def _load_runtime_state(self):
        if not RUNTIME_STATE_FILE.exists():
            return
        try:
            with open(RUNTIME_STATE_FILE, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as error:
            print(f"[platform] Could not load runtime state: {error}")
            return

        self.next_game_id = int(payload.get("next_game_id", self.next_game_id))
        active_game_id = payload.get("active_game_id")
        self.active_game_id = int(active_game_id) if active_game_id is not None else None

        raw_counts = payload.get("instance_player_counts", {})
        self.instance_player_counts = HashTable()
        for game_id, count in raw_counts.items():
            self.instance_player_counts[int(game_id)] = int(count)

        # Restore per-board counters and rebuild corresponding leaderboard entries.
        self.game_counters = HashTable()
        self.game_leaderboards = HashTable()
        for board_name, raw_counter in payload.get("game_counters", {}).items():
            counters = HashTable()
            for username, score in raw_counter.items():
                numeric_score = int(score)
                counters[username] = numeric_score
                self._set_board_score(board_name, username, numeric_score)
            self.game_counters[board_name] = counters

        # Restore match history.
        for username, matches in payload.get("history", {}).items():
            for match in matches:
                self.history.add_match(
                    match.get("game_id"),
                    match.get("players", ()),
                    match.get("winner"),
                )

        # Restore ratings — replay each saved score so averages are correct
        for game_name, scores in payload.get("ratings", {}).items():
            for stars in scores:
                try:
                    self.ratings.rate(game_name, int(stars))
                except Exception:
                    pass