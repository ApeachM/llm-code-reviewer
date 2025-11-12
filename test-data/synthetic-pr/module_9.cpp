#include <iostream>
#include <vector>

// File: module_9.cpp - ResourceManager

class ResourceManager {
private:
    int* resources;
    int count;

public:
    ResourceManager(int n) : count(n) {
        resources = new int[n];
    }

    // No destructor

    int* allocate(int id) {
        // No bounds check
        return &resources[id];
    }

    void deallocate(int* ptr) {
        // Wrong: shouldn't delete individual array elements
        delete ptr;
    }
};

double calculate(int a, int b) {
    return a / b;  // No zero check
}

int main() {
    ResourceManager* rm = new ResourceManager(10);
    int* res = rm->allocate(5);
    *res = 100;
    rm->deallocate(res);  // Double delete risk
    std::cout << calculate(10, 0) << std::endl;
    return 0;
}
