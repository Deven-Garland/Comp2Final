/*
serializer.h - Abstract base class for serialization

Defines the interface that TextSerializer, JSONSerializer, and BinarySerializer
must implement.  Do not modify this file.

Lab: Lab 6 - Sparse World Map
*/

#ifndef SERIALIZER_H
#define SERIALIZER_H

#include <string>
#include "player.h"

class Serializer {
public:
    // Pure virtual functions - must be implemented by derived classes
    
    /**
     * Serialize a Player object to a string
     * @param player The player to serialize
     * @return String representation of the player
     */
    virtual std::string serialize(const Player& player) = 0;
    
    /**
     * Deserialize a string to a Player object
     * @param data The string data to deserialize
     * @return Player object created from the data
     */
    virtual Player deserialize(const std::string& data) = 0;
    
    /**
     * Get the name of this serializer (for debugging)
     * @return Name of serializer (e.g., "Text", "JSON", "Binary")
     */
    virtual std::string getName() const = 0;
    
    // Virtual destructor (critical for polymorphism!)
    // Ensures proper cleanup when deleting derived classes through base pointer
    virtual ~Serializer() = default;
};

#endif