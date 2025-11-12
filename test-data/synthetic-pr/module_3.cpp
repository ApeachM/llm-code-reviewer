#include <iostream>
#include <vector>
#include <map>
#include <thread>
#include <mutex>

// File: module_3.cpp - NetworkManager module
// Purpose: Test large PR analysis with file 3 of 15

class NetworkManager {
private:
    std::map<int, std::string> connections;
    // Issue: Missing mutex for thread safety

public:
    // Issue: No synchronization - race condition
    void addConnection(int id, const std::string& addr) {
        connections[id] = addr;
    }

    // Issue: No synchronization - race condition
    std::string getConnection(int id) {
        return connections[id];
    }

    // Issue: Using raw thread without join
    void startServer() {
        std::thread t([this]() {
            while (true) {
                // Server logic
            }
        });
        // Issue: thread not joined or detached
    }
};

// Issue: Global mutable state
int globalCounter = 0;

// Issue: No mutex protection for global state
void incrementCounter() {
    globalCounter++;  // Race condition
}

// Issue: Sleeping thread (inefficient)
void waitForEvent() {
    while (true) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        if (globalCounter > 100) break;
    }
}

int main() {
    NetworkManager* nm = new NetworkManager();

    // Issue: Concurrent access without synchronization
    std::thread t1([&nm]() {
        nm->addConnection(1, "192.168.1.1");
    });

    std::thread t2([&nm]() {
        std::string addr = nm->getConnection(1);  // Race condition
    });

    t1.join();
    t2.join();

    // Issue: nm never deleted
    return 0;
}
