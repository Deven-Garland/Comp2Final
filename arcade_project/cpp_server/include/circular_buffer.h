/*
circular_buffer.h - Circular buffer (ring buffer) template class

A fixed-size buffer that wraps around when full.
Used as the base for position smoothing strategies.

Author: [Deven Garland]
Date: [2/15/26]
Project: Project 2 - Network Position Buffering
*/

#ifndef CIRCULAR_BUFFER_H
#define CIRCULAR_BUFFER_H

#include <stdexcept>

template<typename T>
class CircularBuffer {
protected:
    T* buffer;           // Array to store elements
    int capacity;        // Maximum number of elements
    int head;            // Index for next dequeue
    int tail;            // Index for next enqueue
    int count;           // Current number of elements
    
public:
    /**
     * Constructor - creates empty circular buffer
     * 
     * @param cap Maximum capacity of the buffer
     */
    CircularBuffer(int cap) {
        // Error checking to make sure buffer is >0
        if (cap <= 0)
            throw std::invalid_argument("Capacity must be greater than 0");
        // Initialize capacity and array to hold values, and set head, tail, and count
        capacity = cap;
        buffer = new T[capacity];
        head = 0;
        tail = 0;
        count = 0;
    }
    
    /**
     * Destructor - clean up allocated memory
     */
    virtual ~CircularBuffer() {
        // Delete memory
        delete[] buffer;
        
    }
    
    /**
     * Add element to the buffer
     * 
     * @param item Element to add
     * @return true if successful, false if buffer is full
     */
    bool enqueue(const T& item) {
        // Checks if the buffer is full
        if (is_full())
            return false;
        // Tail points to where the next element should go, add element there
        buffer[tail] = item;
        // Move tail foward ( move foward 1 position, wrap back to 0 if end is hit)
        tail = (tail +1) % capacity;
        // Keep track of elements stored
        count++;
        return true;
    }
    
    /**
     * Remove and return element from buffer
     * 
     * @return The oldest element in the buffer
     * @throws std::runtime_error if buffer is empty
     */
    T dequeue() {
        // Checks to see if buffer is empty 
        if (is_empty())
            throw std::runtime_error("Buffer is empty");
        // Save the element at the head before we move pointer
        T item = buffer[head];
        // Moves the head to the next position/value
        head = (head + 1) % capacity;
        // Lower amount of elements by 1
        count--;
        // Return removed value 
        return item;
    }
    
    /**
     * Get element at logical index (0 = oldest, size()-1 = newest)
     * 
     * @param index Logical index (0-based from head)
     * @return Element at that position
     * @throws std::out_of_range if index is invalid
     */
    T get(int index) const {
        // Check if the index is in the range of the elements
        if (index < 0 || index >= count)
            throw std::out_of_range("Index out of range");
        // Adjust index relative to head and wrap around if needed
        int actual = (head + index) % capacity;

    // Return the element at that position
     return buffer[actual];
    }
    
    /**
     * Look at the oldest element without removing it
     * 
     * @return The oldest element
     * @throws std::runtime_error if buffer is empty
     */
    T peek() const {
    // Check if the buffer is empty
    if (is_empty())
        throw std::runtime_error("Buffer is empty");

    // Return the oldest element (at head)
    return buffer[head];
    }
    
    /**
     * Check if buffer is empty
     * 
     * @return true if no elements in buffer
     */
    bool is_empty() const {
        // Checks if there are any values in the buffer
        if (count == 0)
            return true;
        return false;
    }
    
    /**
     * Check if buffer is full
     * 
     * @return true if buffer is at capacity
     */
    bool is_full() const {
        // Checks if the values stored are equal to the capacity of the buffer
        return count == capacity;
    }
    
    /**
     * Get current number of elements
     * 
     * @return Number of elements currently in buffer
     */
    int size() const {
        // Returns the amount of elements in buffer
        return count;
    }
    
    /**
     * Get maximum capacity
     * 
     * @return Maximum number of elements buffer can hold
     */
    int get_capacity() const {
        // Returns the size of the buffer
        return capacity;
    }
    
    /**
     * Remove all elements from buffer
     */
    void clear() {
        head = 0;
        tail = 0;
        count = 0;
    }
};

#endif // CIRCULAR_BUFFER_H
