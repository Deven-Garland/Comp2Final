/*
text_serializer.h - Text-based serialization (pipe-delimited)

Format: "id|name|x|y|socket"
Example: "1|Alice|400.5|300.2|5"

Author: [Student Name]
Date: [Date]
*/

#ifndef TEXT_SERIALIZER_H
#define TEXT_SERIALIZER_H

#include "serializer.h"
#include <sstream>

class TextSerializer : public Serializer {
public:
    /**
     * Serialize Player to pipe-delimited string
     * Format: "id|name|x|y|socket"
     */
    std::string serialize(const Player& player) override;
    
    /**
     * Deserialize pipe-delimited string to Player
     * Format: "id|name|x|y|socket"
     */
    Player deserialize(const std::string& data) override;
    
    /**
     * Get serializer name
     */
    std::string getName() const override;
};

#endif
