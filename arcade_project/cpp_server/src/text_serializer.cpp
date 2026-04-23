/*
text_serializer.cpp - Text serialization implementation

Author: [Deven Garland]
Date: [1/28/2026]
*/

#include "text_serializer.h"

#include <sstream>
#include <string>

std::string TextSerializer::serialize(const Player& player) {
    std::ostringstream oss;

    oss << player.get_id() << "|"
        << player.get_name() << "|"
        << player.get_x() << "|"
        << player.get_y() << "|"
        << player.get_socket();

    return oss.str();
}

Player TextSerializer::deserialize(const std::string& data) {
    std::istringstream iss(data);

    std::string id_str, name, x_str, y_str, socket_str;

    std::getline(iss, id_str, '|');
    std::getline(iss, name, '|');
    std::getline(iss, x_str, '|');
    std::getline(iss, y_str, '|');
    std::getline(iss, socket_str);

    int id = std::stoi(id_str);
    int socket = std::stoi(socket_str);
    float x = std::stof(x_str);
    float y = std::stof(y_str);

    return Player(id, name, x, y, socket);
}

std::string TextSerializer::getName() const {
    return "TextSerializer";
}
