/*
player.h - Player class for multiplayer game server

Students implement this file as part of C++ Project 1.

Author: [Student Name]
Date: [Date]
Lab: C++ Project 1 - Player Class & Serialization
*/

#ifndef PLAYER_H
#define PLAYER_H

#include <string>

class Player {
private:
    int id;
    std::string name;
    float x, y;
    int socket;
    bool connected;
    std::string character_type;  // "cleric", "hobbit", "thief", "wizard"
    std::string status;          // "up", "down", "left", "right"
    
public:
    // Constructors
    Player();  // Default constructor
    Player(int id, std::string name, float x, float y, int socket);
    
    // Destructor
    ~Player();
    
    // Getters
    int get_id() const;
    std::string get_name() const;
    float get_x() const;
    float get_y() const;
    int get_socket() const;
    bool is_connected() const;
    std::string get_character_type() const;
    std::string get_status() const;
    
    // Setters
    void set_position(float new_x, float new_y);
    void set_name(std::string new_name);
    void set_connected(bool status);
    void set_socket(int sock);
    void set_character_type(std::string type);
    void set_status(std::string new_status);
    
    // Operators
    bool operator==(const Player& other) const;
};

#endif
