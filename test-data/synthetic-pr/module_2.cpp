#include <iostream>
#include <vector>
#include <string>
#include <memory>

// File: module_2.cpp - FileHandler module
// Purpose: Test large PR analysis with file 2 of 15

class FileHandler {
private:
    char* buffer;  // Issue: raw pointer
    int bufferSize;

public:
    FileHandler(int size) : bufferSize(size) {
        buffer = new char[size];  // Issue: no delete in destructor
    }

    // Issue: Using gets() - deprecated and unsafe
    void readInput() {
        // gets(buffer);  // Extremely dangerous
        std::cin.getline(buffer, bufferSize);  // Better but still raw pointer
    }

    // Issue: No null check before dereference
    void writeData(const char* data) {
        strcpy(buffer, data);  // Issue: no bounds check
    }

    // Issue: Pass vector by value
    std::string joinStrings(std::vector<std::string> strings) {
        std::string result;
        for (auto s : strings) {  // Could use const ref
            result += s;
        }
        return result;
    }
};

// Issue: Function could be const
class Logger {
private:
    std::string logFile;

public:
    Logger(const std::string& file) : logFile(file) {}

    // Issue: Should be const method
    void printLogFile() {
        std::cout << logFile << std::endl;
    }

    // Issue: Returning local variable address
    const char* getLogFileName() {
        std::string name = logFile + ".log";
        return name.c_str();  // Dangling pointer!
    }
};

// Issue: Magic numbers
void processData(int* arr, int size) {
    for (int i = 0; i < size; i++) {
        if (arr[i] > 100) {  // Magic number
            arr[i] = 0;
        }
    }
}

int main() {
    FileHandler* handler = new FileHandler(256);
    handler->writeData("Some data that might overflow");

    Logger log("app");
    log.printLogFile();

    const char* name = log.getLogFileName();  // Issue: dangling pointer
    std::cout << name << std::endl;  // Undefined behavior

    int data[] = {50, 150, 200};
    processData(data, 3);

    // Issue: handler never deleted
    return 0;
}
