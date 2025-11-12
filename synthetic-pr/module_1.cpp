#include <iostream>
#include <vector>
#include <string>
#include <cstring>

// File: module_1.cpp - DataProcessor module
// Purpose: Test large PR analysis with file 1 of 15

class DataProcessor {
private:
    int* data;  // Issue: raw pointer instead of smart pointer
    size_t size;

public:
    // Issue: Missing destructor - memory leak
    DataProcessor(size_t n) : size(n) {
        data = new int[n];
    }

    // Issue: No bounds checking - buffer overflow risk
    int get(size_t index) {
        return data[index];
    }

    // Issue: Pass by value instead of const reference - performance
    void processVector(std::vector<int> v) {
        for (size_t i = 0; i < v.size(); i++) {
            data[i % size] = v[i] * 2;
        }
    }

    // Issue: Raw pointer return without ownership clarity
    int* getData() {
        return data;
    }

    // Issue: Using strcpy (unsafe)
    void setName(char* dest, const char* src) {
        strcpy(dest, src);  // Buffer overflow risk
    }
};

// Issue: Using C-style array parameter
void processArray(int arr[], int size) {
    for (int i = 0; i <= size; i++) {  // Issue: Off-by-one error
        std::cout << arr[i] << std::endl;
    }
}

// Issue: Division by zero not checked
double divide(int a, int b) {
    return static_cast<double>(a) / b;
}

// Issue: String concatenation in loop (inefficient)
std::string buildString(const std::vector<std::string>& parts) {
    std::string result;
    for (int i = 0; i < parts.size(); i++) {
        result = result + parts[i];  // Should use +=
    }
    return result;
}

int main() {
    DataProcessor* proc = new DataProcessor(10);  // Issue: new without delete

    std::vector<int> data = {1, 2, 3, 4, 5};
    proc->processVector(data);

    int arr[5] = {1, 2, 3, 4, 5};
    processArray(arr, 5);

    std::cout << divide(10, 0) << std::endl;  // Issue: Division by zero

    char buffer[10];
    proc->setName(buffer, "This is a very long string that will overflow");

    return 0;  // Issue: Memory leak - proc never deleted
}
