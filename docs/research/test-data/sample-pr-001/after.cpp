// After PR - WITH INTENTIONAL BUGS FOR TESTING
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <thread>

class DataProcessor {
private:
    std::vector<int> data;
    std::string name;
    int* cachedSum;  // BUG: Raw pointer, should be managed

public:
    DataProcessor(std::string n) : name(n), cachedSum(nullptr) {}  // BUG: Pass by value (unnecessary copy)

    void addData(int value) {
        data.push_back(value);
        // Invalidate cache
        if (cachedSum != nullptr) {
            delete cachedSum;
            cachedSum = nullptr;
        }
    }

    int getSum() {
        if (cachedSum != nullptr) {
            return *cachedSum;
        }

        cachedSum = new int(0);  // BUG: Memory leak if exception thrown
        for (size_t i = 0; i < data.size(); i++) {
            *cachedSum += data[i];
        }
        return *cachedSum;
    }

    std::string getName() {  // BUG: Should be const, returns by value
        return name;
    }

    ~DataProcessor() {
        // BUG: Forgot to delete cachedSum!
    }
};

class DataManager {
private:
    std::vector<DataProcessor*> processors;
    DataProcessor* currentProcessor;  // BUG: Dangling pointer risk

public:
    DataManager() : currentProcessor(nullptr) {}

    void addProcessor(const std::string& name) {
        DataProcessor* proc = new DataProcessor(name);
        processors.push_back(proc);
        currentProcessor = proc;  // BUG: Will dangle if vector reallocates
    }

    void processData(int value) {
        // BUG: Inefficient - creates temporary vector on every call
        std::vector<DataProcessor*> temp = processors;
        for (auto proc : temp) {  // BUG: Range-for with raw pointers (not idiomatic)
            proc->addData(value);
        }
    }

    void processDataConcurrently(const std::vector<int>& values) {
        // BUG: Race condition - multiple threads accessing same processors
        std::vector<std::thread> threads;
        for (int val : values) {
            threads.push_back(std::thread([this, val]() {
                for (auto proc : processors) {
                    proc->addData(val);  // BUG: Not thread-safe!
                }
            }));
        }
        for (auto& t : threads) {
            t.join();
        }
    }

    void printResults() {
        for (auto proc : processors) {
            std::cout << proc->getName() << ": " << proc->getSum() << std::endl;
        }
    }

    DataProcessor* getCurrentProcessor() {
        return currentProcessor;  // BUG: Returning raw pointer that can dangle
    }

    ~DataManager() {
        for (auto proc : processors) {
            delete proc;
        }
        // BUG: currentProcessor now dangles if accessed elsewhere
    }
};

// BUG: Memory leak - manager destroyed but pointer escapes
DataProcessor* getProcessor() {
    DataManager manager;
    manager.addProcessor("TempProcessor");
    return manager.getCurrentProcessor();  // BUG: Returns pointer to deleted object!
}

int main() {
    DataManager manager;
    manager.addProcessor("Processor1");
    manager.addProcessor("Processor2");

    for (int i = 1; i <= 10; i++) {
        manager.processData(i);
    }

    // NEW: Concurrent processing
    std::vector<int> batch = {11, 12, 13, 14, 15};
    manager.processDataConcurrently(batch);

    manager.printResults();

    // BUG: Use after free
    DataProcessor* temp = getProcessor();
    std::cout << "Temp: " << temp->getName() << std::endl;  // CRASH!

    return 0;
}
