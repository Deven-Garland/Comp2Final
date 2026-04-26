/*
player.cpp - Player class implementation

Students implement all methods here.

Author: [Student Name]
Date: [Date]
*/

#include "player.h"

// Default constructor
Player::Player() {
    id = 0;
    name = "";
    x = 400.0;
    y = 300.0;
    socket = -1;
    connected = false;
    character_type = "";
    status = "down";
}

// Parameterized constructor
Player::Player(int id, std::string name, float x, float y, int socket) {
    this->id = id;
    this->name = name;
    this->x = x;
    this->y = y;
    this->socket = socket;
    this->connected = true;
    this->character_type = "";
    this->status = "down";
}

// Destructor
Player::~Player() {
    // Nothing to clean up
}

// Getters
int Player::get_id() const {
    return id;
}

std::string Player::get_name() const {
    return name;
}

float Player::get_x() const {
    return x;
}

float Player::get_y() const {
    return y;
}

int Player::get_socket() const {
    return socket;
}

bool Player::is_connected() const {
    return connected;
}

std::string Player::get_character_type() const {
    return character_type;
}

std::string Player::get_status() const {
    return status;
}

// Setters
void Player::set_position(float new_x, float new_y) {
    x = new_x;
    y = new_y;
}

void Player::set_name(std::string new_name) {
    name = new_name;
}

void Player::set_connected(bool status) {
    connected = status;
}

void Player::set_socket(int sock) {
    socket = sock;
}

void Player::set_character_type(std::string type) {
    character_type = type;
}

void Player::set_status(std::string new_status) {
    status = new_status;
}

// Equality operator
bool Player::operator==(const Player& other) const {
    return id == other.id;
}