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
    └── synthetic_dataset/             # CSV files (10,000+ players, 100,000+ sessions)
```

## Running the Arcade (JSON + SSH Tunnel)

This project is run with a remote server workflow:

1. Start the C++ game server on ECE with JSON serialization.
2. Start the Python platform server on ECE.
3. On your laptop, create SSH port forwarding.
4. Run the local client/game process and connect to forwarded localhost ports.

Example SSH forward command:

```bash
ssh -L 8006:localhost:8005 your_username@ece-000.eng.temple.edu -N
```

Then launch a client locally and target `localhost` with the forwarded port.

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