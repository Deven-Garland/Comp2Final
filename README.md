# ECE 3822 Spring 2026 Final Project: Team MOSFET

This is the GitHub repository for Team MOSFET's Computation 2 final project.

## Members
- Deven Garland
- Ellie Lutz
- Kimberly Velasquez
- Mennah Dewidar
- Vraj Patel

## Project Structure

```text

```
Comp2Final/
├─ README.md
├─ AI-WriteUp.txt
├─ client.py
└─ arcade_project/
   ├─ client/
   │  ├─ __init__.py
   │  ├─ arcade_client.py
   │  ├─ connection.py
   │  └─ screens.py
   │
   ├─ platform_server/
   │  ├─ __init__.py
   │  ├─ server.py
   │  ├─ data_ingest.py
   │  ├─ accounts.py
   │  ├─ leaderboard.py
   │  ├─ history.py
   │  ├─ chat.py
   │  ├─ matchmaking.py
   │  ├─ ratings.py
   │  ├─ player_search.py
   │  ├─ playerstats.py
   │  ├─ catalog.py
   │  ├─ API.md
   │  ├─ accounts_data.json
   │  ├─ leaderboard_data.json
   │  ├─ ratings_data.json
   │  ├─ runtime_state.json
   │  └─ test_chat.py
   │
   ├─ datastructures/
   │  ├─ __init__.py
   │  ├─ array.py
   │  ├─ hash_table.py
   │  ├─ linked_list.py
   │  ├─ node.py
   │  ├─ bst.py
   │  ├─ heap.py
   │  ├─ bloom_filter.py
   │  ├─ graph.py
   │  ├─ sparse_matrix.py
   │  ├─ sorting.py
   │  ├─ circular_buffer.py
   │  ├─ stack.py
   │  └─ tests/
   │     ├─ test_hash_table.py
   │     ├─ test_BST.py
   │     ├─ test_heap.py
   │     ├─ test_graph.py
   │     └─ test_bloom_filter.py
   │
   ├─ data/
   │  ├─ generate_data.py
   │  ├─ benchmark_platform_from_csv.py
   │  └─ synthetic_dataset/
   │     ├─ players.csv
   │     ├─ sessions.csv
   │     ├─ chat.csv
   │     └─ games.csv
   │
   ├─ cpp_server/
     ├─ Makefile
     ├─ README.md
     ├─ start_team_servers.sh
     ├─ test_serializers.sh
     ├─ include/
     │  ├─ player.h
     │  ├─ serializer.h
    │  ├─ text_serializer.h
     │  ├─ json_serializer.h
     │  ├─ binary_serializer.h
     │  ├─ game_instance.h
     │  ├─ circular_buffer.h
     │  └─ position_smoother.h
     └─ src/
        ├─ server.cpp
        ├─ player.cpp
        ├─ text_serializer.cpp
        ├─ json_serializer.cpp
        └─ binary_serializer.cpp

## Offline testing (coursework / grading — no live server)

All **dataset load and query benchmarks** run without networking: no `platform_runner.py`, no SSH tunnel, no C++ game server, and no listening TCP socket. The platform is built in-process only.

From `arcade_project`:

```powershell
cd C:\Users\deven\ece3822-spring-assignments\Comp2Final\arcade_project
python .\platform_server\data_ingest.py
```

That entry point delegates to `data/benchmark_platform_from_csv.py` (you can also run that file directly). By default it uses modest row/query caps for a quick laptop run; clear `ARCADE_BENCHMARK_MAX_SESSIONS` and `ARCADE_BENCHMARK_MAX_QUERIES` to run the full synthetic workload (see comments in `benchmark_platform_from_csv.py`).

Offline runs default to **no final write** of `accounts_data.json` / `runtime_state.json` (`ARCADE_OFFLINE_BENCHMARK_NO_DISK=1`). Set that variable to `0` if you want those files updated after a benchmark.

**Unit tests** (also offline): from `arcade_project`, run pytest on `datastructures/tests/` (for example `pytest datastructures/tests`).

### Optional: ingest CSVs into the **live** TCP platform server

This path is only for demos or integration with real clients—not required for graded offline testing.

By default `platform_server/data_ingest.py` in `__main__` runs the **offline** benchmark above; it does **not** attach to a listening server.

To preload CSV rows when you start **`platform_runner.py`** (accounts, history, leaderboard, optional chat sample):

```powershell
cd C:\Users\deven\ece3822-spring-assignments\Comp2Final
$env:ARCADE_INGEST_SYNTHETIC_CSV="1"
# Recommended for a quick test (full files are large and slow on first startup):
$env:ARCADE_INGEST_MAX_PLAYERS="2000"
$env:ARCADE_INGEST_MAX_SESSIONS="3000"
# Optional: `$env:ARCADE_INGEST_CSV_DIR="C:\path\to\synthetic_dataset"`
# Synthetic users log in with password from `$env:ARCADE_SYNTHETIC_PASSWORD` (default `synthetic`)
python .\platform_runner.py
```

After a bulk ingest you may merge with older `leaderboard_data.json` / `runtime_state.json` data unless you archive those files for a clean test.

## Running the Arcade (Exact Working Steps)

This is the exact two-port setup that works for this repo:

- Python platform server on ECE: `50070`
- C++ gameplay server on ECE: `50072`
- Local tunnel ports on laptop: `9000` (platform), `18080` (gameplay)

### 1) Start servers on ECE

Open two terminals on `ece-000`.

Terminal A (C++ gameplay server):

```bash
cd ~/ece3822-spring-assignments/Comp2Final/arcade_project/cpp_server
make SERIALIZER=JSON
./server_json --port 50072
```

Terminal B (Python platform server):

```bash
cd ~/ece3822-spring-assignments/Comp2Final
python3 platform_runner.py
```

You should see:

- `Game Server Started ... Port: 50072 ... Serializer: JSON`
- `Platform server listening on 0.0.0.0:50070`

### 2) Start SSH tunnel on your laptop (Windows PowerShell)

Open a new terminal and keep it open while playing:

```powershell
ssh -o ExitOnForwardFailure=yes -L 9000:127.0.0.1:50070 -L 18080:127.0.0.1:50072 your_username@ece-000.eng.temple.edu -N
```

### 3) Verify tunnel locally

In another local terminal:

```powershell
Test-NetConnection 127.0.0.1 -Port 9000
```

Expected:

- `TcpTestSucceeded : True`

Optional protocol check:

```powershell
python -c "import socket,json; s=socket.create_connection(('127.0.0.1',9000),5); s.sendall((json.dumps({'action':'list_games'})+'\n').encode()); print(s.recv(4096).decode()); s.close()"
```

### 4) Launch the local client

Because gameplay is tunneled to local `18080`, set env vars before launching:

```powershell
cd C:\Users\deven\ece3822-spring-assignments\Comp2Final
$env:ARCADE_GAME_HOST="127.0.0.1"
$env:ARCADE_GAME_PORT="18080"
python .\client.py
```

### 5) Matchmaking behavior

- Queue requires 2 players (`players_per_match=2`), so one client will wait.
- Open a second client and queue to start a match.

### Common issues and fixes

- `Address already in use` on ECE port `50070` or `50072`:

```bash
pkill -f platform_runner.py
pkill -f server_json
pkill -f server_text
```

- `bind [127.0.0.1]:8080: Permission denied` on Windows:
  - Use local port `18080` in tunnel command (already shown above).

- `Could not reach server` on login:
  - Tunnel terminal was closed, or client not pointing at local tunnel endpoint.

- Chat works but game says disconnected:
  - Platform tunnel is fine, but gameplay port mismatch.
  - Ensure `ARCADE_GAME_PORT=18080` before running `client.py`.

## GitHub
https://github.com/Deven-Garland/Comp2Final