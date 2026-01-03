// Verilator-style code with intentional semantic issues for testing
// This simulates a PR that might be submitted to Verilator

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdio>

// Issue 1: Off-by-one error in bit manipulation (similar to V3Number.cpp patterns)
class VNumber {
    std::vector<uint32_t> m_value;
    int m_width;

public:
    VNumber(int width) : m_width(width) {
        m_value.resize((width + 31) / 32, 0);
    }

    // Bug: uses <= instead of < in bit iteration
    void setBits(int lsb, int msb, uint32_t value) {
        for (int i = lsb; i <= msb; i++) {  // Correct for inclusive range
            if (value & (1 << (i - lsb))) {
                m_value[i / 32] |= (1 << (i % 32));
            }
        }
    }

    // Bug: Off-by-one - should be < not <=
    void clearAllBits() {
        for (size_t i = 0; i <= m_value.size(); i++) {  // BUG: out of bounds
            m_value[i] = 0;
        }
    }

    // Bug: Wrong operator in range check
    bool isValidBitRange(int bit) {
        return bit >= 0 || bit < m_width;  // BUG: should be && not ||
    }
};

// Issue 2: Resource leak in error path (similar to V3File.cpp patterns)
class VFileReader {
public:
    bool readFile(const std::string& filename, std::string& content) {
        FILE* fp = fopen(filename.c_str(), "r");
        if (!fp) return false;

        char buffer[4096];
        size_t bytesRead = fread(buffer, 1, sizeof(buffer), fp);

        if (bytesRead == 0) {
            return false;  // BUG: file handle leaked
        }

        content.assign(buffer, bytesRead);
        fclose(fp);
        return true;
    }

    // Correct version for comparison
    bool readFileCorrect(const std::string& filename, std::string& content) {
        FILE* fp = fopen(filename.c_str(), "r");
        if (!fp) return false;

        char buffer[4096];
        size_t bytesRead = fread(buffer, 1, sizeof(buffer), fp);

        if (bytesRead == 0) {
            fclose(fp);  // Correct: close before return
            return false;
        }

        content.assign(buffer, bytesRead);
        fclose(fp);
        return true;
    }
};

// Issue 3: Getter with side effect (semantic inconsistency)
class VOptions {
    std::map<std::string, std::string> m_options;
    mutable int m_accessCount = 0;

public:
    // Bug: getter modifies state
    std::string getOption(const std::string& key) {
        m_accessCount++;  // BUG: side effect in getter
        auto it = m_options.find(key);
        if (it != m_options.end()) return it->second;
        return "";
    }

    void setOption(const std::string& key, const std::string& value) {
        m_options[key] = value;
    }
};

// Issue 4: Missing empty check before division
class VStatistics {
    std::vector<double> m_samples;

public:
    void addSample(double value) {
        m_samples.push_back(value);
    }

    // Bug: No empty check before division
    double getAverage() {
        double sum = 0.0;
        for (const auto& s : m_samples) {
            sum += s;
        }
        return sum / m_samples.size();  // BUG: division by zero if empty
    }

    // Bug: Integer division truncation
    int getPercentile(int n, int total) {
        return n / total * 100;  // BUG: integer division truncates
    }
};

// Issue 5: Incorrect boolean logic in validation
class VValidator {
public:
    // Bug: Should use && instead of ||
    bool isValidRange(int value, int min, int max) {
        return value >= min || value <= max;  // BUG: always true
    }

    // Bug: Negation logic error
    bool isInvalidInput(const std::string& input) {
        return !input.empty() && input.length() > 0;  // Redundant, but not a bug
    }
};

// Clean code for comparison - NO ISSUES
class VCleanExample {
    std::vector<int> m_data;

public:
    void addData(int value) {
        m_data.push_back(value);
    }

    double getAverage() const {
        if (m_data.empty()) return 0.0;  // Correct: empty check
        double sum = 0.0;
        for (const auto& d : m_data) {
            sum += d;
        }
        return sum / m_data.size();
    }

    bool isValidIndex(size_t idx) const {
        return idx < m_data.size();  // Correct: proper bounds check
    }
};
