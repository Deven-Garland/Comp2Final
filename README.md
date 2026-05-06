# ECE 3822 Spring 2026 Final Project: Team MOSFET

This is the GitHub repository for Team MOSFET's Computation 2 final project.

## Members
- Deven Garland
- Ellie Lutz
- Kimberly Velasquez
- Mennah Dewidar
- Vraj Patel

## Project Structure

```
arcade_project/
│
├── client.py                          # Run this to launch the arcade client
│
├── client/
│   ├── arcade_client.py               # Central client class + game loop
│   ├── screens.py                     # All UI screens (Login, Browser, Game, Chat)
│   └── connection.py                  # TCP socket wrappers for both servers
│
├── platform_server/
│   ├── server.py                      # Python platform server entry point
│   ├── accounts.py                    # Player auth (HashTable + BloomFilter)
│   ├── leaderboard.py                 # Score management (BST)
│   ├── chat.py                        # Chat message routing
│   ├── matchmaking.py                 # Waiting queue (MinHeap)
│   └── data_ingest.py                 # Synthetic dataset loader
│
├── datastructures/
│   ├── hash_table.py                  # Custom hash table with chaining
│   ├── bst.py                         # Binary search tree
│   ├── heap.py                        # Min-heap / priority queue
│   ├── bloom_filter.py                # Bloom filter
│   ├── graph.py                       # Directed weighted graph
│   └── sparse_matrix.py              # Sparse matrix (CSR format)
│
├── games/
│   ├── deven_game/game.py
│   ├── ellie_game/game.py
│   ├── kimberly_game/game.py
│   ├── mennah_game/game.py
│   └── vraj_game/game.py
│
├── cpp_server/                        # C++ game server (separate build)
│
├── tests/
│   ├── test_hash_table.py
│   ├── test_bst.py
│   └── test_load.py                   # Stress + complexity benchmarks
│
└── data/
    └── synthetic_dataset/             # CSV files (10,000+ players, 100,000+ sessions, 50,000+ chats, game catalog)
```

### Loading CSV data into the platform server

By default, `platform_server/data_ingest.py` **does not read** those CSV files (it registers three demo users only). Benchmark-style testing without starting the TCP server continues to use `arcade_project/data/benchmark_platform_from_csv.py`.

To actually **ingest CSVs into the live platform server** (accounts, match history rows, leaderboard counters—and optional sampled chat):

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

### Offline synthetic dataset test (no server)

From the `arcade_project` folder, this loads CSVs into an **in-memory** `PlatformServer`, replays sessions, and runs the query benchmark (no TCP):

```powershell
cd C:\Users\deven\ece3822-spring-assignments\Comp2Final\arcade_project
python .\platform_server\data_ingest.py
```

Equivalent script: `arcade_project/data/benchmark_platform_from_csv.py`.## Running the Arcade (Exact Working Steps)

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

## Generating the UML Diagram with pyreverse

Install pylint (includes pyreverse):

```bash
pip install pylint
```

Run from the project root to generate a UML PNG of the Python client:

```bash
pyreverse -o png -p ArcadeClient client/ platform_server/ datastructures/
```

This outputs `classes_ArcadeClient.png` — insert this image into Section 2.2 of the design doc.

To generate just the client classes:

```bash
pyreverse -o png -p Client client/
```

To generate just the data structures:

```bash
pyreverse -o png -p DataStructures datastructures/
```

---

## GitHub
https://github.com/Deven-Garland/Comp2Final