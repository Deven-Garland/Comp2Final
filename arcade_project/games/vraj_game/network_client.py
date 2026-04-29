"""
network_client.py - Network client for multiplayer game

Handles connection to game server with support for three serialization formats:
- TEXT: Pipe-delimited (id|name|x|y|socket)
- JSON: {"id":1,"name":"Alice","x":100,"y":200,"socket":5}
- BINARY: Fixed 88-byte struct

Usage:
    client = NetworkClient("Alice", serializer='json')
    client = NetworkClient("Bob", serializer='json')
    client = NetworkClient("Charlie", serializer='json')
"""

import socket
import threading
import json
from queue import Queue

class NetworkClient:
    def __init__(self, player_name, server_host='localhost', server_port=8080, serializer='json', game_id='vraj'):
        self.player_name = player_name
        self.server_host = server_host
        self.server_port = server_port
        self.serializer = serializer.lower()
        self.game_id = game_id
        
        if self.serializer != 'json':
            raise ValueError(f"Invalid serializer: {serializer}. Must be 'json'")
        
        self.sock = None
        self.connected = False
        self.my_player_id = None
        
        self.update_queue = Queue()
        self.receiver_thread = None
        self.running = False
        
        print(f"Network client using {self.serializer.upper()} serialization")
        
    def connect(self):
        """Connect to game server"""
        try:
            print(f"Connecting to {self.server_host}:{self.server_port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_host, self.server_port))
            self.connected = True
            self.running = True
            
            self.receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receiver_thread.start()
            
            print(f"Connected to server using {self.serializer.upper()} serialization!")
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Background thread to receive messages from server"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    print("Server disconnected")
                    self.connected = False
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._process_message(line)
                    
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                    self.connected = False
                break
    
    def _process_message(self, msg):
        """Process a message from server"""
        # First check message type (before any separator)
        if msg.startswith("CONNECTED|"):
            parts = msg.split('|')
            self.my_player_id = int(parts[1])
            print(f"Assigned player ID: {self.my_player_id}")
            
        elif msg.startswith("STATE|") and "||" in msg:
            # New format: STATE|instance_id||<ser>||...
            # Legacy format: STATE||<ser>||...
            parts = msg.split('||')
            players = {}
            
            for i in range(1, len(parts)):
                if parts[i]:
                    player_data = self._deserialize_player(parts[i])
                    if player_data:
                        players[player_data['id']] = player_data
            self.update_queue.put(players)
    
    def _deserialize_player(self, data):
        """Deserialize player data based on format"""
        try:
            return self._deserialize_json(data)
        except Exception as e:
            print(f"[ERROR] Deserialization error ({self.serializer} format): {e}")
            print(f"[ERROR] Data received: '{data[:100]}...'")
            print(f"[ERROR] This usually means server and client are using different serializers!")
            print(f"[ERROR] Server might be using a different format than '{self.serializer}'")
            return None
    
    def _deserialize_json(self, data):
        """Deserialize JSON format: {"id":1,"name":"Alice",...}"""
        player = json.loads(data)
        return {
            'id': player['id'],
            'name': player['name'],
            'x': player['x'],
            'y': player['y'],
            'character_type': player.get('character_type', ''),
            'status': player.get('status', 'down')
        }
    
    def send_update(self, x, y, character_type="", status="down"):
        """Send our position, character type, and status to server (uses standard UPDATE format)"""
        if self.connected and self.my_player_id is not None:
            msg = f"UPDATE|{self.my_player_id}|{x}|{y}|{self.player_name}|{character_type}|{status}|{self.game_id}\n"
            try:
                self.sock.send(msg.encode('utf-8'))
            except:
                self.connected = False
    
    def get_updates(self):
        """Get most recent update from queue"""
        updates = []
        while not self.update_queue.empty():
            updates.append(self.update_queue.get())
        
        if updates:
            return updates[-1]
        return None
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        self.connected = False
        if self.sock:
            self.sock.close()
