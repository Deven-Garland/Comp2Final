/*
json_serializer.cpp - JSON serialization implementation

Author: [Student Name]
Date: [Date]
*/

#include "json_serializer.h"

std::string JSONSerializer::serialize(const Player& player) {
    std::ostringstream ss;
    ss << "{"
       << "\"id\":" << player.get_id() << ","
       << "\"name\":\"" << player.get_name() << "\","
       << "\"x\":" << player.get_x() << ","
       << "\"y\":" << player.get_y() << ","
       << "\"socket\":" << player.get_socket() << ","
       << "\"character_type\":\"" << player.get_character_type() << "\","
       << "\"status\":\"" << player.get_status() << "\""
       << "}";
    return ss.str();
}

Player JSONSerializer::deserialize(const std::string& data) {
    // Extract fields using helper functions
    int id = extractInt(data, "id");
    std::string name = extractString(data, "name");
    float x = extractFloat(data, "x");
    float y = extractFloat(data, "y");
    int socket = extractInt(data, "socket");
    std::string character_type = extractString(data, "character_type");
    std::string status = extractString(data, "status");
    
    // Create player and set additional fields
    Player player(id, name, x, y, socket);
    player.set_character_type(character_type);
    player.set_status(status);
    
    return player;
}

std::string JSONSerializer::getName() const {
    return "JSON";
}

// Helper function to extract integer from JSON
int JSONSerializer::extractInt(const std::string& json, const std::string& key) {
    std::string search = "\"" + key + "\":";
    size_t pos = json.find(search);
    if (pos == std::string::npos) return 0;
    
    pos += search.length();
    size_t end = json.find_first_of(",}", pos);
    std::string value = json.substr(pos, end - pos);
    
    return std::stoi(value);
}

// Helper function to extract float from JSON
float JSONSerializer::extractFloat(const std::string& json, const std::string& key) {
    std::string search = "\"" + key + "\":";
    size_t pos = json.find(search);
    if (pos == std::string::npos) return 0.0f;
    
    pos += search.length();
    size_t end = json.find_first_of(",}", pos);
    std::string value = json.substr(pos, end - pos);
    
    return std::stof(value);
}

// Helper function to extract string from JSON
std::string JSONSerializer::extractString(const std::string& json, const std::string& key) {
    std::string search = "\"" + key + "\":\"";
    size_t pos = json.find(search);
    if (pos == std::string::npos) return "";
    
    pos += search.length();
    size_t end = json.find("\"", pos);
    
    return json.substr(pos, end - pos);
}