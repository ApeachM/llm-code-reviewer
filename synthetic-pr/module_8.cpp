#include <iostream>
#include <vector>
#include <algorithm>

// File: module_8.cpp - SearchEngine module

class SearchEngine {
private:
    std::vector<std::string>* database;

public:
    SearchEngine() {
        database = new std::vector<std::string>();
    }

    // No destructor - memory leak

    void addEntry(std::string entry) {  // Pass by value
        database->push_back(entry);
    }

    // Inefficient linear search
    bool search(std::string term) {  // Pass by value
        for (int i = 0; i < database->size(); i++) {
            if ((*database)[i].find(term) != std::string::npos) {
                return true;
            }
        }
        return false;
    }

    // Using raw loop instead of algorithm
    void sort() {
        for (size_t i = 0; i < database->size(); i++) {
            for (size_t j = i + 1; j < database->size(); j++) {
                if ((*database)[i] > (*database)[j]) {
                    std::string temp = (*database)[i];
                    (*database)[i] = (*database)[j];
                    (*database)[j] = temp;
                }
            }
        }
    }
};

int main() {
    SearchEngine* se = new SearchEngine();
    se->addEntry("Hello World");
    se->addEntry("Test Entry");
    se->sort();
    std::cout << se->search("Hello") << std::endl;
    return 0;  // Memory leak
}
