#!/usr/bin/env bash
# Start all five team C++ game servers on this machine (e.g. eceserver).
# Each process uses server.cpp --game <name> and binds the default team port
# (see default_port_for_game in src/server.cpp).
#
# Usage:
#   chmod +x start_team_servers.sh
#   ./start_team_servers.sh          # prints PIDs (servers run in background)
#   ./start_team_servers.sh --nohup  # detached mode, PIDs in ./pids.txt
#
# Platform server (Python) registers these five games automatically on start.
# On eceserver set:  --game-host <this_machine_hostname>
# so list_games / get_game_server return the same host + ports for laptops.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

make SERIALIZER=JSON
BIN="./server_json"

if [[ ! -f "$BIN" ]]; then
  echo "Expected binary not found: $BIN (run make from cpp_server first)"
  exit 1
fi

NOHUP_MODE=0
if [[ "${1:-}" == "--nohup" ]]; then
  NOHUP_MODE=1
  : > pids.txt
fi

echo "Using binary: $BIN"
echo "Starting team game servers (mennah deven ellie vraj kimberly)..."

for game in mennah deven ellie vraj kimberly; do
  if [[ "$NOHUP_MODE" -eq 1 ]]; then
    nohup "$BIN" --game "$game" >/dev/null 2>&1 &
    pid=$!
    echo "$pid" >> pids.txt
    echo "  $game -> PID $pid"
  else
    "$BIN" --game "$game" &
    echo "  $game -> PID $!"
  fi
done

if [[ "$NOHUP_MODE" -eq 1 ]]; then
  echo "Done. PIDs in pids.txt"
else
  echo "Background jobs started. Use 'jobs -l' or 'ps' to inspect. This shell will wait on them (Ctrl+C may kill children)."
  wait
fi
