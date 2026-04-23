/*
 * server.cpp - Game server with polymorphic serialization and multi-room instances.
 *
 * One OS process per game title; binds to a single team port. Multiple logical
 * instances (rooms) run in-process: up to 30 players per room. New joins fill
 * the first non-full room or create a new instance. Empty instances are
 * removed after several seconds of no players.
 *
 * Compile: make (TEXT) / make SERIALIZER=JSON / make SERIALIZER=BINARY
 * Run: ./server_text --game deven
 *      ./server_text --port 50064
 * Welcome line: CONNECTED|player_id|instance_id
 * State line:   STATE|instance_id||<ser>||<ser>||...
 * Client UPDATE: same as before: UPDATE|player_id|x|y|name|character_type|status
 */

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <stdexcept>
#include <cstdint>
#include <cerrno>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

#include "player.h"
#include "game_instance.h"
#include "serializer.h"
#include "text_serializer.h"
#include "json_serializer.h"
#include "binary_serializer.h"

#ifdef USE_JSON
    #define SERIALIZER_TYPE JSONSerializer
#elif defined(USE_BINARY)
    #define SERIALIZER_TYPE BinarySerializer
#else
    #define SERIALIZER_TYPE TextSerializer
#endif

static int default_port_for_game(const std::string& g) {
    if (g == "deven") return 50064;
    if (g == "mennah") return 50063;
    if (g == "ellie") return 50072;
    if (g == "kimberly") return 50081;
    if (g == "vraj") return 50077;
    return 8080;
}

static void print_usage(const char* prog) {
    std::cerr
        << "Usage: " << prog << " [--game deven|mennah|ellie|kimberly|vraj] [--port N]\n"
        << "  If --port is omitted, a default team port is used when --game is set.\n"
        << "  Team ports: deven=50064 mennah=50063 ellie=50072 kimberly=50081 vraj=50077\n";
}

class GameServer {
private:
    int server_socket;
    Serializer* serializer;
    std::map<int, GameInstance*> rooms;
    int next_instance_id;
    int next_player_id;
    int port;
    std::string game_label;

    GameInstance* find_or_create_room() {
        for (auto& pair : rooms) {
            if (!pair.second->is_full()) {
                return pair.second;
            }
        }
        const int nid = next_instance_id++;
        GameInstance* g = new GameInstance(nid);
        rooms[nid] = g;
        std::cout << "[INSTANCE] Created instance " << nid << " (active rooms: "
                  << rooms.size() << ")\n";
        return g;
    }

    void tick_empty_instances() {
        std::vector<int> kill;
        for (auto& pr : rooms) {
            if (pr.second->tick_empty_idle()) {
                kill.push_back(pr.first);
            }
        }
        for (int iid : kill) {
            delete rooms[iid];
            rooms.erase(iid);
            std::cout << "[INSTANCE] Destroyed empty instance " << iid
                      << " (active rooms: " << rooms.size() << ")\n";
        }
    }

    int total_players() const {
        int n = 0;
        for (const auto& pr : rooms) {
            n += pr.second->player_count();
        }
        return n;
    }

public:
    GameServer(int port, std::string game_label)
        : port(port), game_label(std::move(game_label)), next_instance_id(1), next_player_id(1) {
        serializer = new SERIALIZER_TYPE();

        server_socket = socket(AF_INET, SOCK_STREAM, 0);
        if (server_socket < 0) {
            std::cerr << "Failed to create socket\n";
            exit(1);
        }

        int opt = 1;
        setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        struct sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(static_cast<std::uint16_t>(port));

        if (bind(server_socket, reinterpret_cast<struct sockaddr*>(&address), sizeof(address)) < 0) {
            std::cerr << "Failed to bind to port " << port << "\n";
            std::cerr << "Error: " << strerror(errno) << "\n";
            exit(1);
        }

        if (listen(server_socket, 64) < 0) {
            std::cerr << "Failed to listen\n";
            exit(1);
        }

        fcntl(server_socket, F_SETFL, O_NONBLOCK);

        std::cout << "======================================\n";
        std::cout << "Game Server (multi-instance)\n";
        std::cout << "======================================\n";
        if (!game_label.empty()) {
            std::cout << "Game tag:  " << game_label << "\n";
        }
        std::cout << "Port:      " << port << "\n";
        std::cout << "Max/room:  " << GameInstance::MAX_PLAYERS_PER_ROOM << " players\n";
        std::cout << "Serializer: " << serializer->getName() << "\n";
        std::cout << "======================================\n";
    }

    ~GameServer() {
        for (auto& pr : rooms) {
            delete pr.second;
        }
        rooms.clear();
        delete serializer;
        close(server_socket);
    }

    void accept_connections() {
        struct sockaddr_in client_addr {};
        socklen_t addr_len = sizeof(client_addr);

        int client_socket = accept(server_socket, reinterpret_cast<struct sockaddr*>(&client_addr), &addr_len);
        if (client_socket < 0) {
            return;
        }

        fcntl(client_socket, F_SETFL, O_NONBLOCK);

        std::cout << "\n[CONNECTION] New client from " << inet_ntoa(client_addr.sin_addr) << "\n";

        const int player_id = next_player_id++;
        const std::string default_name = "Player" + std::to_string(player_id);

        Player* p = new Player(player_id, default_name, 400, 300, client_socket);
        GameInstance* room = find_or_create_room();
        if (!room->try_add_player(p)) {
            std::cerr << "[ERROR] Could not add player to any room; closing socket.\n";
            delete p;
            close(client_socket);
            return;
        }

        const int inst_id = room->get_id();
        const std::string welcome = "CONNECTED|" + std::to_string(player_id) + "|" +
                                    std::to_string(inst_id) + "\n";
        send(client_socket, welcome.c_str(), welcome.length(), 0);

        std::cout << "[PLAYER " << player_id << "] Joined instance " << inst_id
                  << " (" << room->player_count() << "/" << GameInstance::MAX_PLAYERS_PER_ROOM
                  << " in room)\n";
        std::cout << "[STATUS] Total players: " << total_players() << "\n";
    }

    void receive_messages() {
        std::vector<int> disconnected;

        for (auto& pr : rooms) {
            GameInstance* room = pr.second;
            for (const auto& pp : room->get_players()) {
                Player* p = pp.second;
                char buffer[4096];
                const int n = recv(p->get_socket(), buffer, static_cast<int>(sizeof(buffer) - 1), 0);

                if (n > 0) {
                    buffer[n] = '\0';
                    const std::string msg(buffer);

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
                        try {
                            const float new_x = std::stof(x_str);
                            const float new_y = std::stof(y_str);
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
                        } catch (const std::exception&) {
                            // Malformed packet; ignore
                        }
                    }
                } else if (n == 0 || (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK)) {
                    std::cout << "\n[DISCONNECT] Player " << p->get_id() << " (" << p->get_name() << ")\n";
                    close(p->get_socket());
                    disconnected.push_back(p->get_id());
                }
            }
        }

        for (int id : disconnected) {
            for (auto& pr : rooms) {
                if (Player* taken = pr.second->take_player(id)) {
                    std::cout << "[DISCONNECT] Player " << id << " removed from instance " << pr.first
                              << "\n";
                    delete taken;
                    break;
                }
            }
        }

        if (!disconnected.empty()) {
            std::cout << "[STATUS] Total players: " << total_players() << "\n";
        }
    }

    void broadcast_state() {
        for (auto& pr : rooms) {
            GameInstance* room = pr.second;
            if (room->is_empty()) {
                continue;
            }

            std::ostringstream state;
            state << "STATE|" << room->get_id();

            for (const auto& pp : room->get_players()) {
                const std::string serialized = serializer->serialize(*pp.second);
                state << "||" << serialized;
            }
            state << "\n";

            const std::string msg = state.str();
            for (const auto& pp : room->get_players()) {
                Player* p = pp.second;
                send(p->get_socket(), msg.c_str(), msg.length(), 0);
            }
        }
    }

    void print_status() {
        static int counter = 0;
        counter++;

        if (counter % 300 != 0) {
            return;
        }

        std::cout << "\n[STATUS] rooms=" << rooms.size() << " total_players=" << total_players() << "\n";
        for (const auto& pr : rooms) {
            const GameInstance* room = pr.second;
            std::cout << "  - instance " << room->get_id() << ": " << room->player_count() << " players\n";
        }
    }

    void run() {
        std::cout << "\nServer running. Waiting for clients...\n";
        std::cout << "Press Ctrl+C to stop.\n\n";

        while (true) {
            accept_connections();
            receive_messages();
            tick_empty_instances();
            broadcast_state();
            print_status();
            usleep(16666);
        }
    }
};

int main(int argc, char* argv[]) {
    int port = 8080;
    bool have_port = false;
    std::string game;

    for (int i = 1; i < argc; i++) {
        const std::string arg = argv[i];
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        }
        if ((arg == "--port" || arg == "-p") && i + 1 < argc) {
            port = std::atoi(argv[i + 1]);
            have_port = true;
            i++;
        } else if (arg == "--game" && i + 1 < argc) {
            game = argv[i + 1];
            i++;
        }
    }

    if (!have_port) {
        port = default_port_for_game(game);
    }

    if (port <= 0 || port > 65535) {
        std::cerr << "Invalid port " << port << "\n";
        return 1;
    }

    if (game.empty()) {
        std::cout << "Note: pass --game deven|mennah|ellie|kimberly|vraj to use team default port.\n";
    }

    GameServer server(port, game);
    server.run();
    return 0;
}
