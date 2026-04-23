/*
position_smoother.h - Position smoothing using circular buffer

Smooths network position updates by averaging recent positions.
Reduces visual jitter with minimal added latency.

Author: [Deven Garland]
Date: [2/25/26]
Project: Project 2 - Network Position Buffering
*/

#ifndef POSITION_SMOOTHER_H
#define POSITION_SMOOTHER_H

#include "circular_buffer.h"
#include "position.h"  // Position struct
#include <cmath>

/**
 * Position smoother using averaging strategies
 * 
 * Inherits from CircularBuffer to store recent positions.
 * Provides different averaging strategies to smooth movement.
 */
class PositionSmoother : public CircularBuffer<Position> {
public:
    /**
     * Constructor
     * 
     * @param buffer_size Number of recent positions to keep (default: 5)
     */
    PositionSmoother(int buffer_size = 5);
    
    /**
     * Add a new position to the buffer
     * 
     * @param x X coordinate
     * @param y Y coordinate
     * @param timestamp Time when position was received (optional)
     */
    void add_position(float x, float y, long timestamp = 0);
    
    /**
     * Get simple average of all positions in buffer
     * 
     * Averages all positions equally (each has same weight).
     * 
     * @return Averaged position
     * @throws std::runtime_error if buffer is empty
     */
    Position get_simple_average() const;
    
    /**
     * Get weighted average - recent positions weighted more heavily
     * 
     * Oldest position gets weight 1, next gets weight 2, ..., newest gets weight N.
     * This makes recent positions matter more than old positions.
     * 
     * Example with 3 positions:
     *   Oldest (index 0): weight 1
     *   Middle (index 1): weight 2
     *   Newest (index 2): weight 3
     *   Total weight: 1 + 2 + 3 = 6
     *   Weighted avg = (pos0*1 + pos1*2 + pos2*3) / 6
     * 
     * @return Weighted averaged position
     * @throws std::runtime_error if buffer is empty
     */
    Position get_weighted_average() const;
    
    /**
     * Get exponentially smoothed position (bonus)
     * 
     * Uses exponential moving average formula:
     *   smoothed = alpha * newest + (1-alpha) * previous_smoothed
     * 
     * Higher alpha = more responsive (follows new positions quickly)
     * Lower alpha = more smooth (changes slowly)
     * 
     * @param alpha Smoothing factor (0.0 to 1.0, default 0.3)
     * @return Exponentially smoothed position
     * @throws std::runtime_error if buffer is empty
     */
    Position get_exponential_smooth(float alpha = 0.3f) const;
    
    /**
     * Get the most recent (newest) position without smoothing
     * 
     * @return Most recent position
     * @throws std::runtime_error if buffer is empty
     */
    Position get_latest() const;
    
    /**
     * Calculate current variance/jitter in the buffer
     * 
     * Useful for measuring how much positions are jumping around.
     * Higher variance = more jitter.
     * 
     * @return Standard deviation of positions
     */
    float get_variance() const;
};

#endif // POSITION_SMOOTHER_H