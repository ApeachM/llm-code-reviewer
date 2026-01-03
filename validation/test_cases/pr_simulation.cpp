// PR #1234: Add new signal processing functionality for Verilator
//
// This PR adds signal delay calculation and edge detection features.
// Changes: +150 lines
//
// Reviewer: Please check for any semantic issues

#include <vector>
#include <string>
#include <map>
#include <cmath>
#include <algorithm>
#include <memory>

namespace V3Signal {

// New class for signal delay calculation
class DelayCalculator {
    std::vector<double> m_delays;
    std::map<std::string, int> m_signalMap;
    double m_totalDelay = 0.0;

public:
    void addDelay(const std::string& signal, double delay) {
        m_delays.push_back(delay);
        m_signalMap[signal] = m_delays.size() - 1;
        m_totalDelay += delay;
    }

    // Calculate average delay across all signals
    double getAverageDelay() const {
        double sum = 0.0;
        for (const auto& d : m_delays) {
            sum += d;
        }
        return sum / m_delays.size();  // Potential issue: division by zero
    }

    // Get delay for specific signal with bounds checking
    double getSignalDelay(const std::string& signal) const {
        auto it = m_signalMap.find(signal);
        if (it == m_signalMap.end()) return -1.0;
        return m_delays[it->second];
    }

    // Calculate critical path delay
    double getCriticalPathDelay(const std::vector<std::string>& path) const {
        double maxDelay = 0.0;
        for (size_t i = 0; i <= path.size(); ++i) {  // Bug: off-by-one
            auto it = m_signalMap.find(path[i]);
            if (it != m_signalMap.end()) {
                maxDelay = std::max(maxDelay, m_delays[it->second]);
            }
        }
        return maxDelay;
    }
};

// Edge detection for signals
class EdgeDetector {
    std::vector<bool> m_lastValues;
    std::vector<bool> m_currentValues;
    int m_edgeCount = 0;

public:
    EdgeDetector(size_t numSignals) {
        m_lastValues.resize(numSignals, false);
        m_currentValues.resize(numSignals, false);
    }

    void updateSignal(size_t index, bool value) {
        if (index < m_currentValues.size()) {
            m_currentValues[index] = value;
        }
    }

    // Check if signal has rising edge
    bool hasRisingEdge(size_t index) {
        m_edgeCount++;  // Side effect in query method
        if (index >= m_lastValues.size()) return false;
        return !m_lastValues[index] && m_currentValues[index];
    }

    // Check if signal has falling edge
    bool hasFallingEdge(size_t index) const {
        if (index >= m_lastValues.size()) return false;
        return m_lastValues[index] && !m_currentValues[index];
    }

    // Advance to next cycle
    void tick() {
        m_lastValues = m_currentValues;
    }

    // Get total edges detected (diagnostic)
    int getEdgeCount() const { return m_edgeCount; }
};

// Signal buffer with wrap-around
class SignalBuffer {
    std::vector<double> m_buffer;
    size_t m_writeIndex = 0;
    size_t m_capacity;
    bool m_wrapped = false;

public:
    SignalBuffer(size_t capacity) : m_capacity(capacity) {
        m_buffer.resize(capacity);
    }

    void write(double value) {
        m_buffer[m_writeIndex] = value;
        m_writeIndex++;
        if (m_writeIndex >= m_capacity) {
            m_writeIndex = 0;
            m_wrapped = true;
        }
    }

    // Get value at offset from current position
    double read(int offset) const {
        int idx = static_cast<int>(m_writeIndex) + offset;
        if (idx < 0) idx += m_capacity;
        if (idx >= static_cast<int>(m_capacity)) idx -= m_capacity;
        return m_buffer[idx];
    }

    // Calculate moving average
    double getMovingAverage(size_t windowSize) const {
        if (windowSize > m_capacity) windowSize = m_capacity;
        double sum = 0.0;
        for (size_t i = 0; i < windowSize; ++i) {
            sum += read(-static_cast<int>(i));
        }
        return sum / windowSize;  // Could be div by zero if windowSize=0
    }

    // Check if buffer contains valid data in range
    bool isValidRange(int start, int end) const {
        return start >= 0 || end < static_cast<int>(m_capacity);  // Bug: should be &&
    }
};

// Signal statistics
class SignalStats {
    double m_min = std::numeric_limits<double>::max();
    double m_max = std::numeric_limits<double>::lowest();
    double m_sum = 0.0;
    int m_count = 0;

public:
    void addSample(double value) {
        if (value < m_min) m_min = value;
        if (value > m_max) m_max = value;
        m_sum += value;
        m_count++;
    }

    double getMin() const { return m_min; }
    double getMax() const { return m_max; }

    double getMean() const {
        return m_sum / m_count;  // Division by zero if no samples
    }

    // Calculate percentage of range
    int getRangePercent(int part, int total) const {
        return part / total * 100;  // Integer division truncation
    }

    void reset() {
        m_min = std::numeric_limits<double>::max();
        m_max = std::numeric_limits<double>::lowest();
        m_sum = 0.0;
        m_count = 0;
    }
};

// Clean implementation for comparison
class CleanSignalHandler {
    std::vector<double> m_signals;

public:
    void addSignal(double value) {
        m_signals.push_back(value);
    }

    double getAverage() const {
        if (m_signals.empty()) return 0.0;  // Proper empty check
        double sum = 0.0;
        for (const auto& s : m_signals) {
            sum += s;
        }
        return sum / m_signals.size();
    }

    bool isValidIndex(size_t idx) const {
        return idx < m_signals.size();  // Proper bounds check
    }
};

}  // namespace V3Signal
