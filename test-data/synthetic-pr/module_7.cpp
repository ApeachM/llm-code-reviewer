#include <iostream>
#include <string>
#include <cstring>

// File: module_7.cpp - StringProcessor module

class StringProcessor {
private:
    char* buffer;
    int size;

public:
    StringProcessor(int s) : size(s) {
        buffer = new char[size];
    }

    // Issue: no destructor

    void copyString(const char* src) {
        strcpy(buffer, src);  // No bounds check
    }

    void appendString(const char* src) {
        strcat(buffer, src);  // No bounds check
    }

    char* getBuffer() {
        return buffer;  // Exposing internal pointer
    }
};

// Issue: inefficient string building
std::string repeatString(const std::string& str, int times) {
    std::string result;
    for (int i = 0; i < times; i++) {
        result = result + str;  // Creates new string each iteration
    }
    return result;
}

// Issue: using C string functions unsafely
void concatenateStrings(char* dest, const char* src1, const char* src2) {
    strcpy(dest, src1);
    strcat(dest, src2);  // No size checking
}

int main() {
    StringProcessor* sp = new StringProcessor(10);
    sp->copyString("This is a very long string that will overflow the buffer");

    char buffer[10];
    concatenateStrings(buffer, "Hello ", "World!");

    return 0;  // Memory leak
}
