#include <iostream>
#include <memory>
#include <vector>

// File: module_6.cpp - CacheManager module

class CacheManager {
private:
    int* cache;
    size_t capacity;

public:
    CacheManager(size_t cap) : capacity(cap) {
        cache = new int[cap];
        // Issue: uninitialized memory
    }

    // Issue: no destructor

    int get(size_t index) {
        // Issue: no bounds check
        return cache[index];
    }

    void set(size_t index, int value) {
        // Issue: no bounds check
        cache[index] = value;
    }

    // Issue: copy constructor not defined - double delete risk
};

void processCache(CacheManager cache) {  // Issue: pass by value with raw pointer
    cache.set(0, 42);
}

int main() {
    CacheManager* cm = new CacheManager(100);
    cm->set(150, 10);  // Buffer overflow

    processCache(*cm);  // Dangerous

    return 0;  // Memory leak
}
