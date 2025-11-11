// Base version - Before PR
#include <iostream>
#include <vector>
#include <string>
#include <memory>

class DataProcessor {
private:
    std::vector<int> data;
    std::string name;

public:
    DataProcessor(const std::string& n) : name(n) {}

    void addData(int value) {
        data.push_back(value);
    }

    int getSum() const {
        int sum = 0;
        for (size_t i = 0; i < data.size(); i++) {
            sum += data[i];
        }
        return sum;
    }

    std::string getName() const {
        return name;
    }
};

class DataManager {
private:
    std::vector<DataProcessor*> processors;

public:
    void addProcessor(const std::string& name) {
        processors.push_back(new DataProcessor(name));
    }

    void processData(int value) {
        for (auto proc : processors) {
            proc->addData(value);
        }
    }

    void printResults() {
        for (auto proc : processors) {
            std::cout << proc->getName() << ": " << proc->getSum() << std::endl;
        }
    }

    ~DataManager() {
        for (auto proc : processors) {
            delete proc;
        }
    }
};

int main() {
    DataManager manager;
    manager.addProcessor("Processor1");
    manager.addProcessor("Processor2");

    for (int i = 1; i <= 10; i++) {
        manager.processData(i);
    }

    manager.printResults();
    return 0;
}
