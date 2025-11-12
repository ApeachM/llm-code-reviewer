#include <iostream>
#include <vector>

// Example with intentional bugs for testing
class DataProcessor {
private:
    int* data;
    std::vector<int> values;

public:
    DataProcessor(int size) {
        data = new int[size];  // BUG: Memory leak - never deleted
        for (int i = 0; i < size; i++) {
            data[i] = i;
        }
    }

    void processData(std::vector<int> input) {  // BUG: Pass by value (copy)
        for (int i = 0; i < input.size(); i++) {  // BUG: Use range-for
            values.push_back(input[i]);
        }
    }

    void printData() {
        for (auto val : values) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    // BUG: Missing destructor - memory leak!
};

int main() {
    DataProcessor processor(10);

    std::vector<int> input = {1, 2, 3, 4, 5};
    processor.processData(input);

    processor.printData();

    return 0;
    // BUG: processor's memory (data array) is never freed
}
