#include <iostream>
#include <thread>
#include <vector>

// File: module_13.cpp - ThreadManager

int sharedCounter = 0;  // Global mutable state

class ThreadManager {
public:
    void incrementCounter() {
        sharedCounter++;  // No synchronization
    }

    void spawnThreads() {
        std::vector<std::thread> threads;
        for (int i = 0; i < 10; i++) {
            threads.push_back(std::thread([this]() {
                incrementCounter();
            }));
        }
        // Threads not joined - undefined behavior
    }
};

void accessSharedData() {
    for (int i = 0; i < 1000; i++) {
        sharedCounter++;  // Race condition
    }
}

int main() {
    ThreadManager tm;
    tm.spawnThreads();

    std::thread t1(accessSharedData);
    std::thread t2(accessSharedData);

    t1.join();
    t2.join();

    std::cout << sharedCounter << std::endl;
    return 0;
}
