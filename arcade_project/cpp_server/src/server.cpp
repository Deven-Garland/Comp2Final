/*
server.cpp - Game server with polymorphic serialization

Compile with different serializers:
  make SERIALIZER=TEXT    (default)
  make SERIALIZER=JSON
  make SERIALIZER=BINARY

Run:
  ./server_text           (for TEXT)
  ./server_json           (for JSON)
  ./server_binary         (for BINARY)
*/

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

#include "player.h"
#include "serializer.h"
#include "text_serializer.h"
#include "json_serializer.h"
#include "binary_serializer.h"

// Compile-time serializer selection
#ifdef USE_JSON
    #define SERIALIZER_TYPE JSONSerializer
#elif defined(USE_BINARY)
    #define SERIALIZER_TYPE BinarySerializer
#else
    #define SERIALIZER_TYPE TextSerializer
#endif

class GameServer {
private:
    int server_socket;
    std::map<int, Player*> players;
    Serializer* serializer;  // Polymorphic serializer!
    int next_player_id = 1;
    int port;
    
public:
    GameServer(int port) : port(port) {
        // Create serializer based on compile flag
        serializer = new SERIALIZER_TYPE();
        
        // Create socket
        server_socket = socket(AF_INET, SOCK_STREAM, 0);
        if (server_socket < 0) {
            std::cerr << "Failed to create socket\n";
            exit(1);
        }
        
        // Allow reuse of address
        int opt = 1;
        setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        
        // Bind to port
        struct sockaddr_in address;
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(port);
        
        if (bind(server_socket, (struct sockaddr*)&address, sizeof(address)) < 0) {
            std::cerr << "Failed to bind to port " << port << "\n";
            std::cerr << "Error: " << strerror(errno) << "\n";
            exit(1);
        }
        
        // Listen
        if (listen(server_socket, 10) < 0) {
            std::cerr << "Failed to listen\n";
            exit(1);
        }
        
        // Set non-blocking
        fcntl(server_socket, F_SETFL, O_NONBLOCK);
        
        std::cout << "======================================\n";
        std::cout << "Game Server Started\n";
        std::cout << "======================================\n";
        std::cout << "Port: " << port << "\n";
        std::cout << "Serializer: " << serializer->getName() << "\n";
        std::cout << "======================================\n";
    }
    
    ~GameServer() {
        for (auto& pair : players) {
            delete pair.second;
        }
        delete serializer;
        close(server_socket);
    }
    
    void accept_connections() {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        
        int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &addr_len);
        
        if (client_socket >= 0) {
            fcntl(client_socket, F_SETFL, O_NONBLOCK);
            
            std::cout << "\n[CONNECTION] New client from " << inet_ntoa(client_addr.sin_addr) << "\n";
            
            int player_id = next_player_id++;
            std::string default_name = "Player" + std::to_string(player_id);
            
            Player* p = new Player(player_id, default_name, 400, 300, client_socket);
            players[player_id] = p;
            
            // Send welcome with player ID
            std::string welcome = "CONNECTED|" + std::to_string(player_id) + "\n";
            send(client_socket, welcome.c_str(), welcome.length(), 0);
            
            std::cout << "[PLAYER " << player_id << "] Connected (socket: " << client_socket << ")\n";
            std::cout << "[STATUS] Total players: " << players.size() << "\n";
        }
    }
    
    void receive_messages() {
        std::vector<int> disconnected;
        
        for (auto& pair : players) {
            Player* p = pair.second;
            char buffer[4096];
            
            int n = recv(p->get_socket(), buffer, sizeof(buffer) - 1, 0);
            
            if (n > 0) {
                buffer[n] = '\0';
                std::string msg(buffer);
                
                // Parse: "UPDATE|player_id|x|y|name|character_type|status"
                std::istringstream ss(msg);
                std::string type, id_str, x_str, y_str, name, character_type, status;
                
                std::getline(ss, type, '|');
                std::getline(ss, id_str, '|');
                std::getline(ss, x_str, '|');
                std::getline(ss, y_str, '|');
                std::getline(ss, name, '|');
                std::getline(ss, character_type, '|');
                std::getline(ss, status);
                
                if (type == "UPDATE") {
                    float new_x = std::stof(x_str);
                    float new_y = std::stof(y_str);
                    p->set_position(new_x, new_y);
                    
                    if (!name.empty() && name != p->get_name()) {
                        p->set_name(name);
                    }
                    
                    if (!character_type.empty()) {
                        p->set_character_type(character_type);
                    }
                    
                    if (!status.empty()) {
                        p->set_status(status);
                    }
                }
            } else if (n == 0 || (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) {
                std::cout << "\n[DISCONNECT] Player " << p->get_id() 
                          << " (" << p->get_name() << ")\n";
                close(p->get_socket());
                disconnected.push_back(p->get_id());
            }
        }
        
        for (int id : disconnected) {
            delete players[id];
            players.erase(id);
            std::cout << "[STATUS] Total players: " << players.size() << "\n";
        }
    }
    
    void broadcast_state() {
        if (players.empty()) {
            return;
        }
        
        // Build state using serializer!
        // Format: STATE||<player1_serialized>||<player2_serialized>||...
        // Using || as separator to avoid conflicts with any serialization format
        std::ostringstream state;
        state << "STATE";
        
        for (auto& pair : players) {
            Player* p = pair.second;
            // Use polymorphic serialize()!
            std::string serialized = serializer->serialize(*p);
            state << "||" << serialized;
        }
        state << "\n";
        
        std::string msg = state.str();
        
        // Send to all
        for (auto& pair : players) {
            Player* p = pair.second;
            send(p->get_socket(), msg.c_str(), msg.length(), 0);
        }
    }
    
    void print_status() {
        static int counter = 0;
        counter++;
        
        if (counter % 300 == 0) {
            std::cout << "\n[STATUS] Running... Players: " << players.size() << "\n";
            for (auto& pair : players) {
                Player* p = pair.second;
                std::cout << "  - Player " << p->get_id() << ": " << p->get_name() 
                          << " at (" << p->get_x() << ", " << p->get_y() << ")\n";
            }
        }
    }
    
    void run() {
        std::cout << "\nServer running on port " << port << "\n";
        std::cout << "Using " << serializer->getName() << " serialization\n";
        std::cout << "Waiting for clients...\n";
        std::cout << "Press Ctrl+C to stop.\n\n";
        
        while (true) {
            accept_connections();
            receive_messages();
            broadcast_state();
            print_status();
            
            usleep(16666);  // ~60 FPS
        }
    }
};

int main(int argc, char* argv[]) {
    int port = 8080;
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--port" || arg == "-p") {
            if (i + 1 < argc) {
                port = std::atoi(argv[i + 1]);
                i++;
            }
        }
    }
    
    GameServer server(port);
    server.run();
    
    return 0;
}