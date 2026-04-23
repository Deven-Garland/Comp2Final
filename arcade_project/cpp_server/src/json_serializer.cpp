/*
json_serializer.cpp - JSON serialization implementation

Author: [Deven Garland]
Date: [2/1/2026]
*/

#include "json_serializer.h"

#include <sstream>
#include <string>

std::string JSONSerializer::serialize(const Player& player) {
    std::ostringstream oss;

    oss << "{";
    oss << "\"id\":" << player.get_id();
    oss << ",\"name\":\"" << player.get_name() << "\"";
    oss << ",\"x\":" << player.get_x();
    oss << ",\"y\":" << player.get_y();
    oss << ",\"socket\":" << player.get_socket();
    oss << "}";

    return oss.str();
}

Player JSONSerializer::deserialize(const std::string& data) {
    int id = extractInt(data, "id");
    std::string name = extractString(data, "name");
    float x = extractFloat(data, "x");
    float y = extractFloat(data, "y");
    int socket = extractInt(data, "socket");

    return Player(id, name, x, y, socket);
}

std::string JSONSerializer::getName() const {
    return "JSON";
}

// Helper function to extract integer from JSON
int JSONSerializer::extractInt(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\":";
    size_t keyPos = json.find(searchKey);

    if (keyPos == std::string::npos) {
        return 0;
    }

    size_t valueStart = keyPos + searchKey.length();
    size_t valueEnd = json.find_first_of(",}", valueStart);

    std::string value = json.substr(valueStart, valueEnd - valueStart);
    return std::stoi(value);
}

// Helper function to extract float from JSON
float JSONSerializer::extractFloat(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\":";
    size_t keyPos = json.find(searchKey);

    if (keyPos == std::string::npos) {
        return 0.0f;
    }

    size_t valueStart = keyPos + searchKey.length();
    size_t valueEnd = json.find_first_of(",}", valueStart);

    std::string value = json.substr(valueStart, valueEnd - valueStart);
    return std::stof(value);
}

// Helper function to extract string from JSON
std::string JSONSerializer::extractString(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\":\"";
    size_t keyPos = json.find(searchKey);

    if (keyPos == std::string::npos) {
        return "";
    }

    size_t valueStart = keyPos + searchKey.length();
    size_t valueEnd = json.find("\"", valueStart);

    return json.substr(valueStart, valueEnd - valueStart);
}
