/*
binary_serializer.h - Binary serialization (packed struct)

Format: Fixed 88-byte struct
  [4 bytes: id][32 bytes: name][4 bytes: x][4 bytes: y][4 bytes: socket][40 bytes: padding]

Author: [Student Name]
Date: [Date]
*/

#ifndef BINARY_SERIALIZER_H
#define BINARY_SERIALIZER_H

#include "serializer.h"
#include <cstring>

class BinarySerializer : public Serializer {
private:
    // Binary format struct
    struct PlayerData {
        int id;              // 4 bytes
        char name[32];       // 32 bytes
        float x;             // 4 bytes
        float y;             // 4 bytes
        int socket;          // 4 bytes
        char character_type[16];  // 16 bytes (e.g., "wizard", "cleric")
        char status[8];      // 8 bytes (e.g., "up", "down")
        char padding[16];    // 16 bytes (for future expansion)
        // Total: 88 bytes
    };
    
public:
    /**
     * Serialize Player to binary format (88 bytes)
     */
    std::string serialize(const Player& player) override;
    
    /**
     * Deserialize binary data (88 bytes) to Player
     */
    Player deserialize(const std::string& data) override;
    
    /**
     * Get serializer name
     */
    std::string getName() const override;
};

#endif
