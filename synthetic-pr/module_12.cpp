#include <iostream>
#include <vector>

// File: module_12.cpp - VectorProcessor

class VectorProcessor {
public:
    std::vector<int>* process(std::vector<int> input) {  // Pass by value
        std::vector<int>* result = new std::vector<int>();
        for (auto val : input) {
            result->push_back(val * 2);
        }
        return result;  // Caller must delete
    }

    int getElement(std::vector<int>& vec, int index) {
        return vec[index];  // No bounds check
    }
};

void modifyVector(std::vector<int> vec) {  // Pass by value
    vec.push_back(100);  // Doesn't modify original
}

int main() {
    VectorProcessor vp;
    std::vector<int> data = {1, 2, 3};
    std::vector<int>* result = vp.process(data);
    std::cout << vp.getElement(*result, 10) << std::endl;  // Out of bounds
    modifyVector(data);
    return 0;  // result never deleted
}
