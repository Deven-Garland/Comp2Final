# Platform API 

This is the network API your clients use to talk to the platform.

## 1) How Requests And Responses Work

- Transport: TCP + newline-delimited JSON
- Send one JSON object per line
- Use `action` to choose what the server should do
- Response always comes back in this wrapper:
  - success: `{"ok": true, "request_id": "...", "result": ...}`
  - error: `{"ok": false, "request_id": "...", "error": "..."}`

### Request examples

```json
{"action":"login","username":"alice","password":"pw123"}
```

```json
{"action":"top_players","params":{"k":10,"game":"deven","stat":"score"}}
```

## 2) Message Types

### Auth

- `register(username, password)` -> `bool`
- `login(username, password)` -> `bool`

### Match + Session

- `join_queue(username)` -> `bool`
- `try_create_match()` -> `null` or `{"game_id": int, "players": [..]}`
- `instance_status(game_id)` -> `{"game_id": int, "current_players": int, "max_players": int}`
- `end_game(game_id, players, winner, score, game="global")` -> `true`
- `record_session_result(game, username, score=0, play_time=0, chats_delta=0, deaths_delta=0, disconnects_delta=0)` -> `bool`
- `player_disconnected(username, game="global")` -> `bool`
- `player_died(username, game="global")` -> `bool`

### Game Discovery / Routing

- `list_games(sort_by="popularity", descending=true)` -> `[{"name": str, "host": str, "port": int, "popularity": int, "rating": float, "recency": int}, ...]`
- `get_game_server(game)` -> `{"name": str, "host": str, "port": int}`
- `send_game_request(game, request)` -> forwarded game-server response

### Chat

- `send_message(game_id, username, text, game="global")` -> `true`
- `get_chat(game_id)` -> `{"messages":[{"sender": str, "message": str, "time": str}, ...]}`

### Leaderboard + Ratings

- `top_players(k, game=None, stat=None)` -> top players list
- `player_rank(username, game, stat="score")` -> `int` or `null`
- `players_in_score_range(game, stat, low, high)` -> list
- `rate_game(game_name, stars)` -> `true`
- `get_rating_rankings()` -> rankings list
- `get_highest_rated_game()` -> game/rating entry
- `get_lowest_rated_game()` -> game/rating entry

### Profile / Stats / Search

- `player_history(username, sort_by="date", descending=true)` -> player match history sorted by `date`, `duration`, or `score`
- `search_players(prefix)` -> matching profile list
- `get_player_profile(username)` -> profile object or `null`
- `set_favorite(username, game_id)` -> bool-like result
- `get_favorite(username)` -> favorite game value
- `add_minutes(username, minutes)` -> bool-like result
- `get_minutes(username)` -> int
- `get_messages_sent(username)` -> int

## 3) Expected Error Behavior

- bad JSON -> `invalid JSON: ...`
- bad params/type mismatch -> `bad request parameters: ...`
- unknown action -> `unknown request type: ...`
- domain errors (example: unknown game) -> error string from server exception

## 4) Resilience Checklist (Extra Credit)

- malformed JSON does not crash server
- missing params does not crash server
- wrong param types return clean error
- unknown action returns clean error
- high-volume chat/leaderboard requests stay responsive
- every response includes `ok`, and includes `request_id` when supplied

