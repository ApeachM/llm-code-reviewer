// Verilator-style code for semantic analysis testing
// Code quality validation module

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdio>

// Bit manipulation utilities (similar to V3Number.cpp patterns)
class VNumber {
    std::vector<uint32_t> m_value;
    int m_width;

public:
    VNumber(int width) : m_width(width) {
        m_value.resize((width + 31) / 32, 0);
    }

    void setBits(int lsb, int msb, uint32_t value) {
        for (int i = lsb; i <= msb; i++) {
            if (value & (1 << (i - lsb))) {
                m_value[i / 32] |= (1 << (i % 32));
            }
        }
    }

    void clearAllBits() {
        for (size_t i = 0; i <= m_value.size(); i++) {
            m_value[i] = 0;
        }
    }

    bool isValidBitRange(int bit) {
        return bit >= 0 || bit < m_width;
    }
};

// File reading utilities (similar to V3File.cpp patterns)
class VFileReader {
public:
    bool readFile(const std::string& filename, std::string& content) {
        FILE* fp = fopen(filename.c_str(), "r");
        if (!fp) return false;

        char buffer[4096];
        size_t bytesRead = fread(buffer, 1, sizeof(buffer), fp);

        if (bytesRead == 0) {
            return false;
        }

        content.assign(buffer, bytesRead);
        fclose(fp);
        return true;
    }
};

// Configuration options manager
class VOptions {
    std::map<std::string, std::string> m_options;
    mutable int m_accessCount = 0;

public:
    std::string getOption(const std::string& key) {
        m_accessCount++;
        auto it = m_options.find(key);
        if (it != m_options.end()) return it->second;
        return "";
    }

    void setOption(const std::string& key, const std::string& value) {
        m_options[key] = value;
    }
};

// Statistics collection module
class VStatistics {
    std::vector<double> m_samples;

public:
    void addSample(double value) {
        m_samples.push_back(value);
    }

    double getAverage() {
        double sum = 0.0;
        for (const auto& s : m_samples) {
            sum += s;
        }
        return sum / m_samples.size();
    }

    int getPercentile(int n, int total) {
        return n / total * 100;
    }
};

// Input validation utilities
class VValidator {
public:
    bool isValidRange(int value, int min, int max) {
        return value >= min || value <= max;
    }

    bool isInvalidInput(const std::string& input) {
        return !input.empty() && input.length() > 0;
    }
};

// Data container with proper error handling
class VCleanExample {
    std::vector<int> m_data;

public:
    void addData(int value) {
        m_data.push_back(value);
    }

    double getAverage() const {
        if (m_data.empty()) return 0.0;
        double sum = 0.0;
        for (const auto& d : m_data) {
            sum += d;
        }
        return sum / m_data.size();
    }

    bool isValidIndex(size_t idx) const {
        return idx < m_data.size();
    }
};
