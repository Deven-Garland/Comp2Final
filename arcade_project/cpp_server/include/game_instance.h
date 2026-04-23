/*
 * game_instance.h - One match / room inside a game server process.
 * Max 30 players per room; empty rooms are removed after an idle period.
 */

#ifndef GAME_INSTANCE_H
#define GAME_INSTANCE_H

#include <map>
#include "player.h"

class GameInstance {
public:
    static constexpr int MAX_PLAYERS_PER_ROOM = 30;
    // ~5 seconds at ~60 server ticks per second
    static constexpr int EMPTY_ROOM_IDLE_TICKS = 300;

    explicit GameInstance(int instance_id) : id(instance_id), empty_idle_ticks(0) {}

    ~GameInstance() {
        for (auto& pr : players) {
            delete pr.second;
        }
        players.clear();
    }

    int get_id() const { return id; }

    int player_count() const { return static_cast<int>(players.size()); }

    bool is_full() const { return player_count() >= MAX_PLAYERS_PER_ROOM; }

    bool is_empty() const { return players.empty(); }

    bool try_add_player(Player* p) {
        if (is_full()) {
            return false;
        }
        p->set_instance_id(id);
        players[p->get_id()] = p;
        empty_idle_ticks = 0;
        return true;
    }

    void remove_player(int player_id) {
        auto it = players.find(player_id);
        if (it != players.end()) {
            it->second->set_instance_id(-1);
            players.erase(it);
        }
    }

    // Remove from this room and return the pointer (caller may delete), or nullptr.
    Player* take_player(int player_id) {
        auto it = players.find(player_id);
        if (it == players.end()) {
            return nullptr;
        }
        Player* p = it->second;
        p->set_instance_id(-1);
        players.erase(it);
        return p;
    }

    const std::map<int, Player*>& get_players() const { return players; }

    // Call once per server tick. Returns true if this instance should be destroyed.
    bool tick_empty_idle() {
        if (!is_empty()) {
            empty_idle_ticks = 0;
            return false;
        }
        empty_idle_ticks++;
        return empty_idle_ticks >= EMPTY_ROOM_IDLE_TICKS;
    }

private:
    int id;
    std::map<int, Player*> players;
    int empty_idle_ticks;
};

#endif
