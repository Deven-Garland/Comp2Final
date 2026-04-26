/*
binary_serializer.cpp - Binary serialization implementation

NOTE: Binary data must be base64-encoded for safe text transmission!
Base64 encoding/decoding functions are provided below.

Author: [Student Name]
Date: [Date]
*/

#include "binary_serializer.h"

// Base64 encoding table
static const char base64_chars[] = 
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789+/";

// Helper: Base64 encode (PROVIDED - use as-is)
std::string base64_encode(const unsigned char* data, size_t len) {
    std::string ret;
    int i = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];

    while (len--) {
        char_array_3[i++] = *(data++);
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for(i = 0; i < 4; i++)
                ret += base64_chars[char_array_4[i]];
            i = 0;
        }
    }

    if (i) {
        for(int j = i; j < 3; j++)
            char_array_3[j] = '\0';

        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);

        for (int j = 0; j < i + 1; j++)
            ret += base64_chars[char_array_4[j]];

        while(i++ < 3)
            ret += '=';
    }

    return ret;
}

// Helper: Base64 decode (PROVIDED - use as-is)
std::string base64_decode(const std::string& encoded_string) {
    size_t in_len = encoded_string.size();
    int i = 0;
    int in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    std::string ret;

    while (in_len-- && (encoded_string[in_] != '=')) {
        if (!isalnum(encoded_string[in_]) && encoded_string[in_] != '+' && encoded_string[in_] != '/') {
            in_++;
            continue;
        }

        char_array_4[i++] = encoded_string[in_]; in_++;
        if (i == 4) {
            for (i = 0; i < 4; i++)
                char_array_4[i] = strchr(base64_chars, char_array_4[i]) - base64_chars;

            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

            for (i = 0; i < 3; i++)
                ret += char_array_3[i];
            i = 0;
        }
    }

    if (i) {
        for (int j = i; j < 4; j++)
            char_array_4[j] = 0;

        for (int j = 0; j < 4; j++)
            char_array_4[j] = strchr(base64_chars, char_array_4[j]) - base64_chars;

        char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);

        for (int j = 0; j < i - 1; j++)
            ret += char_array_3[j];
    }

    return ret;
}

std::string BinarySerializer::serialize(const Player& player) {
    PlayerData pd;
    
    // Initialize all fields to zero
    memset(&pd, 0, sizeof(PlayerData));
    
    // Copy simple fields
    pd.id = player.get_id();
    pd.x = player.get_x();
    pd.y = player.get_y();
    pd.socket = player.get_socket();
    
    // Copy name (max 31 chars, null-terminate at position 31)
    strncpy(pd.name, player.get_name().c_str(), 31);
    pd.name[31] = '\0';
    
    // Copy character_type (max 15 chars, null-terminate at position 15)
    strncpy(pd.character_type, player.get_character_type().c_str(), 15);
    pd.character_type[15] = '\0';
    
    // Copy status (max 7 chars, null-terminate at position 7)
    strncpy(pd.status, player.get_status().c_str(), 7);
    pd.status[7] = '\0';
    
    // Convert struct to bytes
    const unsigned char* bytes = reinterpret_cast<const unsigned char*>(&pd);
    
    // Base64-encode the bytes
    return base64_encode(bytes, sizeof(PlayerData));
}

Player BinarySerializer::deserialize(const std::string& data) {
    // Base64-decode the input string
    std::string decoded = base64_decode(data);
    
    // Check if we have enough data
    if (decoded.size() < sizeof(PlayerData)) {
        return Player();
    }
    
    // Convert bytes back to struct
    const PlayerData* pd = reinterpret_cast<const PlayerData*>(decoded.data());
    
    // Extract fields
    int id = pd->id;
    std::string name(pd->name);
    float x = pd->x;
    float y = pd->y;
    int socket = pd->socket;
    std::string character_type(pd->character_type);
    std::string status(pd->status);
    
    // Create player and set additional fields
    Player player(id, name, x, y, socket);
    player.set_character_type(character_type);
    player.set_status(status);
    
    return player;
}

std::string BinarySerializer::getName() const {
    return "Binary";
}