#include <iostream>
#include <vector>
#include <algorithm>

// File: module_15.cpp - AlgorithmMisuse

class DataSorter {
public:
    // Reinventing std::sort
    void bubbleSort(std::vector<int>& vec) {
        for (size_t i = 0; i < vec.size(); i++) {
            for (size_t j = 0; j < vec.size() - 1; j++) {
                if (vec[j] > vec[j + 1]) {
                    int temp = vec[j];
                    vec[j] = vec[j + 1];
                    vec[j + 1] = temp;
                }
            }
        }
    }

    // Not using std::find
    bool contains(const std::vector<int>& vec, int value) {
        for (size_t i = 0; i < vec.size(); i++) {
            if (vec[i] == value) return true;
        }
        return false;
    }

    // Not using std::count
    int countOccurrences(const std::vector<int>& vec, int value) {
        int count = 0;
        for (size_t i = 0; i < vec.size(); i++) {
            if (vec[i] == value) count++;
        }
        return count;
    }
};

// Not using range-based for loop
void printAll(const std::vector<int>& vec) {
    for (std::vector<int>::const_iterator it = vec.begin();
         it != vec.end(); ++it) {
        std::cout << *it << " ";
    }
}

// Manual memory management when containers would work
int* createDynamicArray(int size) {
    int* arr = new int[size];
    for (int i = 0; i < size; i++) {
        arr[i] = i;
    }
    return arr;  // Caller must delete
}

int main() {
    DataSorter sorter;
    std::vector<int> data = {5, 2, 8, 1, 9};

    sorter.bubbleSort(data);
    std::cout << sorter.contains(data, 5) << std::endl;
    std::cout << sorter.countOccurrences(data, 2) << std::endl;

    printAll(data);

    int* arr = createDynamicArray(10);
    // Never deleted - memory leak

    return 0;
}
