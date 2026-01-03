#include <iostream>
#include <vector>
#include <algorithm>

// File: module_5.cpp - DataAnalyzer module
// Purpose: Test large PR analysis with file 5 of 15

class DataAnalyzer {
private:
    std::vector<double>* data;  // Issue: should use value, not pointer

public:
    DataAnalyzer() {
        data = new std::vector<double>();  // Issue: unnecessary new
    }

    // Issue: No destructor - memory leak

    // Issue: O(n²) algorithm when O(n) possible
    void removeDuplicates() {
        for (size_t i = 0; i < data->size(); i++) {
            for (size_t j = i + 1; j < data->size(); j++) {
                if ((*data)[i] == (*data)[j]) {
                    data->erase(data->begin() + j);
                }
            }
        }
    }

    // Issue: Pass large object by value
    void mergeData(std::vector<double> newData) {
        for (auto val : newData) {
            data->push_back(val);
        }
    }

    // Issue: Inefficient search - linear instead of binary
    bool contains(double value) {
        for (size_t i = 0; i < data->size(); i++) {
            if ((*data)[i] == value) return true;
        }
        return false;
    }
};

// Issue: Using raw loop instead of algorithm
int sumArray(int* arr, int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;  // Could use std::accumulate
}

// Issue: Not using auto for iterator
void printVector(const std::vector<int>& vec) {
    for (std::vector<int>::const_iterator it = vec.begin(); it != vec.end(); ++it) {
        std::cout << *it << " ";
    }
}

int main() {
    DataAnalyzer* analyzer = new DataAnalyzer();

    std::vector<double> data = {1.0, 2.0, 3.0, 2.0, 4.0};
    analyzer->mergeData(data);
    analyzer->removeDuplicates();

    int arr[] = {1, 2, 3, 4, 5};
    std::cout << sumArray(arr, 5) << std::endl;

    // Issue: analyzer never deleted
    return 0;
}
