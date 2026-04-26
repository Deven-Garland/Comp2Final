#!/bin/bash

# test_serializers.sh - Automated testing script for Project 1
# 
# This script tests your serializer implementations before integrating with the server.
# Run this FIRST to catch bugs early!
#
# Usage:
#   chmod +x test_serializers.sh
#   ./test_serializers.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Print header
echo ""
echo "=========================================="
echo "  Project 1 Serializer Testing Suite"
echo "=========================================="
echo ""

# Function to print test result
print_result() {
    local test_name="$1"
    local result="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Check if we're in the right directory
if [ ! -f "Makefile" ]; then
    echo -e "${RED}Error: Makefile not found!${NC}"
    echo "Please run this script from the code/server/ directory"
    exit 1
fi

# Check if required files exist
echo -e "${BLUE}[1/5] Checking required files...${NC}"
FILES=("include/player.h" "src/player.cpp" "include/serializer.h" 
       "include/text_serializer.h" "src/text_serializer.cpp"
       "include/json_serializer.h" "src/json_serializer.cpp"
       "include/binary_serializer.h" "src/binary_serializer.cpp")

all_files_exist=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_result "Found $file" "PASS"
    else
        print_result "Found $file" "FAIL"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo -e "${RED}Missing required files. Please implement all files before testing.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/5] Compiling TEXT serializer...${NC}"
make clean > /dev/null 2>&1
if make SERIALIZER=TEXT > /dev/null 2>&1; then
    print_result "Compile TEXT serializer" "PASS"
    TEXT_COMPILED=true
else
    print_result "Compile TEXT serializer" "FAIL"
    echo -e "${YELLOW}Compilation errors:${NC}"
    make SERIALIZER=TEXT
    TEXT_COMPILED=false
fi

echo ""
echo -e "${BLUE}[3/5] Compiling JSON serializer...${NC}"
make clean > /dev/null 2>&1
if make SERIALIZER=JSON > /dev/null 2>&1; then
    print_result "Compile JSON serializer" "PASS"
    JSON_COMPILED=true
else
    print_result "Compile JSON serializer" "FAIL"
    echo -e "${YELLOW}Compilation errors:${NC}"
    make SERIALIZER=JSON
    JSON_COMPILED=false
fi

echo ""
echo -e "${BLUE}[4/5] Compiling BINARY serializer...${NC}"
make clean > /dev/null 2>&1
if make SERIALIZER=BINARY > /dev/null 2>&1; then
    print_result "Compile BINARY serializer" "PASS"
    BINARY_COMPILED=true
else
    print_result "Compile BINARY serializer" "FAIL"
    echo -e "${YELLOW}Compilation errors:${NC}"
    make SERIALIZER=BINARY
    BINARY_COMPILED=false
fi

# Create a simple C++ test program
echo ""
echo -e "${BLUE}[5/5] Running unit tests...${NC}"

cat > test_unit.cpp << 'EOF'
#include <iostream>
#include <cassert>
#include <cmath>
#include "player.h"
#include "text_serializer.h"
#include "json_serializer.h"
#include "binary_serializer.h"

bool floatsEqual(float a, float b) {
    return std::fabs(a - b) < 0.001f;
}

int main() {
    int passed = 0;
    int failed = 0;
    
    // Test Player class
    std::cout << "\nTesting Player class..." << std::endl;
    
    // Test default constructor
    try {
        Player p1;
        if (p1.get_id() == 0 && p1.get_name() == "" && 
            floatsEqual(p1.get_x(), 400.0f) && floatsEqual(p1.get_y(), 300.0f) &&
            p1.get_socket() == -1 && !p1.is_connected()) {
            std::cout << "  ✓ Default constructor" << std::endl;
            passed++;
        } else {
            std::cout << "  ✗ Default constructor (values incorrect)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ Default constructor (exception thrown)" << std::endl;
        failed++;
    }
    
    // Test parameterized constructor
    try {
        Player p2(42, "Alice", 100.5f, 200.3f, 5);
        if (p2.get_id() == 42 && p2.get_name() == "Alice" &&
            floatsEqual(p2.get_x(), 100.5f) && floatsEqual(p2.get_y(), 200.3f) &&
            p2.get_socket() == 5 && p2.is_connected()) {
            std::cout << "  ✓ Parameterized constructor" << std::endl;
            passed++;
        } else {
            std::cout << "  ✗ Parameterized constructor (values incorrect)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ Parameterized constructor (exception thrown)" << std::endl;
        failed++;
    }
    
    // Test setters
    try {
        Player p3(1, "Test", 0, 0, 0);
        p3.set_position(300.7f, 400.9f);
        p3.set_name("Bob");
        p3.set_connected(false);
        p3.set_socket(10);
        
        if (floatsEqual(p3.get_x(), 300.7f) && floatsEqual(p3.get_y(), 400.9f) &&
            p3.get_name() == "Bob" && !p3.is_connected() && p3.get_socket() == 10) {
            std::cout << "  ✓ Setters" << std::endl;
            passed++;
        } else {
            std::cout << "  ✗ Setters (values incorrect)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ Setters (exception thrown)" << std::endl;
        failed++;
    }
    
    // Test equality operator
    try {
        Player p4(42, "Test1", 0, 0, 0);
        Player p5(42, "Test2", 100, 200, 5);
        Player p6(99, "Test3", 0, 0, 0);
        
        if (p4 == p5 && !(p4 == p6)) {
            std::cout << "  ✓ Equality operator" << std::endl;
            passed++;
        } else {
            std::cout << "  ✗ Equality operator (logic incorrect)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ Equality operator (exception thrown)" << std::endl;
        failed++;
    }
    
    // Create test player for serializers
    Player testPlayer(1, "Alice", 400.5f, 300.2f, 5);
    
    // Test TEXT serializer
    std::cout << "\nTesting TEXT serializer..." << std::endl;
    try {
        TextSerializer textSer;
        std::string serialized = textSer.serialize(testPlayer);
        
        if (!serialized.empty()) {
            std::cout << "  ✓ TEXT serialize (produces output)" << std::endl;
            std::cout << "    Output: " << serialized << std::endl;
            passed++;
            
            // Test deserialize
            try {
                Player restored = textSer.deserialize(serialized);
                if (restored.get_id() == 1 && restored.get_name() == "Alice" &&
                    floatsEqual(restored.get_x(), 400.5f) && floatsEqual(restored.get_y(), 300.2f) &&
                    restored.get_socket() == 5) {
                    std::cout << "  ✓ TEXT round-trip (deserialize works)" << std::endl;
                    passed++;
                } else {
                    std::cout << "  ✗ TEXT round-trip (values incorrect after deserialize)" << std::endl;
                    std::cout << "    Expected: id=1, name=Alice, x=400.5, y=300.2, socket=5" << std::endl;
                    std::cout << "    Got: id=" << restored.get_id() << ", name=" << restored.get_name() 
                              << ", x=" << restored.get_x() << ", y=" << restored.get_y() 
                              << ", socket=" << restored.get_socket() << std::endl;
                    failed++;
                }
            } catch (...) {
                std::cout << "  ✗ TEXT deserialize (exception thrown)" << std::endl;
                failed++;
            }
        } else {
            std::cout << "  ✗ TEXT serialize (empty output)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ TEXT serialize (exception thrown)" << std::endl;
        failed++;
    }
    
    // Test JSON serializer
    std::cout << "\nTesting JSON serializer..." << std::endl;
    try {
        JSONSerializer jsonSer;
        std::string serialized = jsonSer.serialize(testPlayer);
        
        if (!serialized.empty()) {
            std::cout << "  ✓ JSON serialize (produces output)" << std::endl;
            std::cout << "    Output: " << serialized << std::endl;
            passed++;
            
            // Test deserialize
            try {
                Player restored = jsonSer.deserialize(serialized);
                if (restored.get_id() == 1 && restored.get_name() == "Alice" &&
                    floatsEqual(restored.get_x(), 400.5f) && floatsEqual(restored.get_y(), 300.2f) &&
                    restored.get_socket() == 5) {
                    std::cout << "  ✓ JSON round-trip (deserialize works)" << std::endl;
                    passed++;
                } else {
                    std::cout << "  ✗ JSON round-trip (values incorrect after deserialize)" << std::endl;
                    std::cout << "    Expected: id=1, name=Alice, x=400.5, y=300.2, socket=5" << std::endl;
                    std::cout << "    Got: id=" << restored.get_id() << ", name=" << restored.get_name() 
                              << ", x=" << restored.get_x() << ", y=" << restored.get_y() 
                              << ", socket=" << restored.get_socket() << std::endl;
                    failed++;
                }
            } catch (...) {
                std::cout << "  ✗ JSON deserialize (exception thrown)" << std::endl;
                failed++;
            }
        } else {
            std::cout << "  ✗ JSON serialize (empty output)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ JSON serialize (exception thrown)" << std::endl;
        failed++;
    }
    
    // Test BINARY serializer
    std::cout << "\nTesting BINARY serializer..." << std::endl;
    try {
        BinarySerializer binSer;
        std::string serialized = binSer.serialize(testPlayer);
        
        if (!serialized.empty()) {
            std::cout << "  ✓ BINARY serialize (produces output)" << std::endl;
            std::cout << "    Output: [" << serialized.size() << " bytes of base64 data]" << std::endl;
            passed++;
            
            // Test deserialize
            try {
                Player restored = binSer.deserialize(serialized);
                if (restored.get_id() == 1 && restored.get_name() == "Alice" &&
                    floatsEqual(restored.get_x(), 400.5f) && floatsEqual(restored.get_y(), 300.2f) &&
                    restored.get_socket() == 5) {
                    std::cout << "  ✓ BINARY round-trip (deserialize works)" << std::endl;
                    passed++;
                } else {
                    std::cout << "  ✗ BINARY round-trip (values incorrect after deserialize)" << std::endl;
                    std::cout << "    Expected: id=1, name=Alice, x=400.5, y=300.2, socket=5" << std::endl;
                    std::cout << "    Got: id=" << restored.get_id() << ", name=" << restored.get_name() 
                              << ", x=" << restored.get_x() << ", y=" << restored.get_y() 
                              << ", socket=" << restored.get_socket() << std::endl;
                    failed++;
                }
            } catch (...) {
                std::cout << "  ✗ BINARY deserialize (exception thrown)" << std::endl;
                failed++;
            }
        } else {
            std::cout << "  ✗ BINARY serialize (empty output)" << std::endl;
            failed++;
        }
    } catch (...) {
        std::cout << "  ✗ BINARY serialize (exception thrown)" << std::endl;
        failed++;
    }
    
    // Print summary
    std::cout << "\n==========================================" << std::endl;
    std::cout << "Test Results:" << std::endl;
    std::cout << "  Passed: " << passed << std::endl;
    std::cout << "  Failed: " << failed << std::endl;
    std::cout << "  Total:  " << (passed + failed) << std::endl;
    std::cout << "==========================================" << std::endl;
    
    if (failed == 0) {
        std::cout << "\n✓ All tests passed! Your implementation looks good." << std::endl;
        std::cout << "Next step: Test with the actual server and Python clients." << std::endl;
        return 0;
    } else {
        std::cout << "\n✗ Some tests failed. Please fix the issues above." << std::endl;
        return 1;
    }
}
EOF

# Compile and run unit tests
if g++ -std=c++17 -I include -o test_unit test_unit.cpp \
    src/player.cpp src/text_serializer.cpp src/json_serializer.cpp src/binary_serializer.cpp > /dev/null 2>&1; then
    
    print_result "Compile unit tests" "PASS"
    echo ""
    
    # Run the unit tests
    if ./test_unit; then
        UNIT_TESTS_PASSED=true
    else
        UNIT_TESTS_PASSED=false
    fi
    
    # Clean up
    rm -f test_unit test_unit.cpp
else
    print_result "Compile unit tests" "FAIL"
    echo -e "${YELLOW}Unit test compilation failed. Check your implementations.${NC}"
    rm -f test_unit.cpp
    UNIT_TESTS_PASSED=false
fi

# Final summary
echo ""
echo "=========================================="
echo "  Final Summary"
echo "=========================================="
echo -e "Compilation tests: ${TESTS_PASSED}/${TOTAL_TESTS} passed"

if [ "$UNIT_TESTS_PASSED" = true ]; then
    echo -e "Unit tests: ${GREEN}PASSED${NC}"
else
    echo -e "Unit tests: ${RED}FAILED${NC}"
fi

echo ""
if [ "$TESTS_FAILED" -eq 0 ] && [ "$UNIT_TESTS_PASSED" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "  ✓ ALL TESTS PASSED!"
    echo "==========================================${NC}"
    echo ""
    echo "Your serializers are working correctly!"
    echo ""
    echo "Next steps:"
    echo "  1. Test with the actual server:"
    echo "     make SERIALIZER=TEXT"
    echo "     ./server_text"
    echo ""
    echo "  2. Run Python clients (in another terminal):"
    echo "     cd ../game/"
    echo "     python main.py Alice --serializer text"
    echo ""
    echo "  3. Repeat for JSON and BINARY serializers"
    echo ""
    exit 0
else
    echo -e "${RED}=========================================="
    echo "  ✗ SOME TESTS FAILED"
    echo "==========================================${NC}"
    echo ""
    echo "Please fix the issues above before testing with the server."
    echo ""
    exit 1
fi