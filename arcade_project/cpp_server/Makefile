# Makefile for C++ Project 1 - Multiplayer Game Server
#
# Directory structure:
#   include/  - Header files (.h)
#   src/      - Source files (.cpp)
#
# Usage:
#   make                    # Compile with TEXT serializer (default)
#   make SERIALIZER=TEXT    # Compile with TEXT serializer
#   make SERIALIZER=JSON    # Compile with JSON serializer
#   make SERIALIZER=BINARY  # Compile with BINARY serializer
#   make clean              # Remove all compiled files
#
# This creates: server_text, server_json, or server_binary

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -I include

# Serializer selection (default: TEXT)
SERIALIZER ?= TEXT

ifeq ($(SERIALIZER), JSON)
    CXXFLAGS += -DUSE_JSON
    SUFFIX = _json
else ifeq ($(SERIALIZER), BINARY)
    CXXFLAGS += -DUSE_BINARY
    SUFFIX = _binary
else
    # Default to TEXT (no flag needed)
    SUFFIX = _text
endif

# Source and object directories (serializer-specific objects)
SRC_DIR = src
OBJ_DIR = obj$(SUFFIX)

# Create obj directory if it doesn't exist
$(shell mkdir -p $(OBJ_DIR))

# Object files (will be placed in obj_text/, obj_json/, or obj_binary/)
OBJS = $(OBJ_DIR)/player.o $(OBJ_DIR)/text_serializer.o \
       $(OBJ_DIR)/json_serializer.o $(OBJ_DIR)/binary_serializer.o

# Default target
all: server$(SUFFIX)

# Link server
server$(SUFFIX): $(SRC_DIR)/server.cpp $(OBJS)
	$(CXX) $(CXXFLAGS) -o server$(SUFFIX) $(SRC_DIR)/server.cpp $(OBJS)
	@echo ""
	@echo "===================================="
	@echo "Server compiled successfully!"
	@echo "===================================="
	@echo "Serializer: $(SERIALIZER)"
	@echo "Executable: server$(SUFFIX)"
	@echo ""
	@echo "Run with:"
	@echo "  ./server$(SUFFIX) --game deven"
	@echo "  ./server$(SUFFIX) --port 50064"
	@echo "  Team defaults: deven=50064 mennah=50063 ellie=50072 kimberly=50081 vraj=50077"
	@echo "===================================="
	@echo ""

# Compile object files
$(OBJ_DIR)/player.o: $(SRC_DIR)/player.cpp include/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/player.cpp -o $(OBJ_DIR)/player.o

$(OBJ_DIR)/text_serializer.o: $(SRC_DIR)/text_serializer.cpp include/text_serializer.h include/serializer.h include/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/text_serializer.cpp -o $(OBJ_DIR)/text_serializer.o

$(OBJ_DIR)/json_serializer.o: $(SRC_DIR)/json_serializer.cpp include/json_serializer.h include/serializer.h include/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/json_serializer.cpp -o $(OBJ_DIR)/json_serializer.o

$(OBJ_DIR)/binary_serializer.o: $(SRC_DIR)/binary_serializer.cpp include/binary_serializer.h include/serializer.h include/player.h
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/binary_serializer.cpp -o $(OBJ_DIR)/binary_serializer.o

# Clean up
clean:
	rm -rf obj_text obj_json obj_binary server_text server_json server_binary
	@echo "Cleaned up all compiled files and object directories"

# Phony targets
.PHONY: all clean