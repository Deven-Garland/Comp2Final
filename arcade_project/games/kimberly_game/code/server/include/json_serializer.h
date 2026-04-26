/*
json_serializer.h - JSON serialization

Format: {"id":1,"name":"Alice","x":400.5,"y":300.2,"socket":5}

Author: [Student Name]
Date: [Date]
*/

#ifndef JSON_SERIALIZER_H
#define JSON_SERIALIZER_H

#include "serializer.h"
#include <sstream>

class JSONSerializer : public Serializer {
public:
    /**
     * Serialize Player to JSON string
     * Format: {"id":1,"name":"Alice","x":400.5,"y":300.2,"socket":5}
     */
    std::string serialize(const Player& player) override;
    
    /**
     * Deserialize JSON string to Player
     */
    Player deserialize(const std::string& data) override;
    
    /**
     * Get serializer name
     */
    std::string getName() const override;

private:
    // Helper functions for parsing JSON (students implement these)
    int extractInt(const std::string& json, const std::string& key);
    float extractFloat(const std::string& json, const std::string& key);
    std::string extractString(const std::string& json, const std::string& key);
};

#endif
