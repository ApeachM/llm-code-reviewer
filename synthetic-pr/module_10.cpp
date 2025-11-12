#include <iostream>
#include <map>

// File: module_10.cpp - SessionManager

class SessionManager {
private:
    std::map<int, std::string>* sessions;

public:
    SessionManager() {
        sessions = new std::map<int, std::string>();
    }

    // No destructor

    void createSession(int id, std::string data) {
        (*sessions)[id] = data;
    }

    std::string getSession(int id) {
        return (*sessions)[id];  // No check if exists
    }
};

int* createArray() {
    int arr[10] = {1, 2, 3};
    return arr;  // Returning local array address
}

int main() {
    SessionManager* sm = new SessionManager();
    sm->createSession(1, "user_data");
    int* arr = createArray();  // Dangling pointer
    std::cout << arr[0] << std::endl;  // Undefined behavior
    return 0;
}
