#include <iostream>
#include <string>
#include <vector>

// File: module_4.cpp - ConfigParser module
// Purpose: Test large PR analysis with file 4 of 15

class ConfigParser {
private:
    char* configData;
    size_t dataSize;

public:
    ConfigParser() : dataSize(1024) {
        configData = (char*)malloc(dataSize);  // Issue: mixing malloc with C++
    }

    ~ConfigParser() {
        delete[] configData;  // Issue: delete[] with malloc - should use free()
    }

    // Issue: Buffer overflow vulnerability
    void parseConfig(const char* filename) {
        FILE* f = fopen(filename, "r");  // Issue: no error check
        fread(configData, 1, 2048, f);  // Issue: reading more than allocated
        fclose(f);
    }

    // Issue: Returning pointer to internal data
    char* getRawConfig() {
        return configData;  // No const, allows modification
    }
};

// Issue: Hardcoded credentials
const char* DB_PASSWORD = "admin123";  // Security issue
const char* API_KEY = "sk-1234567890abcdef";  // Security issue

// Issue: SQL injection vulnerability
std::string buildQuery(const std::string& userInput) {
    return "SELECT * FROM users WHERE name='" + userInput + "'";  // SQL injection
}

// Issue: No input validation
void processUserInput(const std::string& input) {
    // Directly using user input without validation
    system(input.c_str());  // Command injection vulnerability
}

int main() {
    ConfigParser* parser = new ConfigParser();
    parser->parseConfig("/etc/config.txt");

    std::string query = buildQuery("admin' OR '1'='1");
    std::cout << query << std::endl;

    // Issue: parser never deleted
    return 0;
}
