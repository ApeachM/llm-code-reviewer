#include <iostream>
#include <memory>

// File: module_14.cpp - SmartPointerMisuse

class DataHolder {
private:
    int* data;

public:
    DataHolder(int val) {
        data = new int(val);
    }

    ~DataHolder() {
        delete data;
    }

    // No copy constructor - double delete risk
    // No move constructor
};

void mixedPointerUsage() {
    int* raw = new int(42);
    std::shared_ptr<int> shared(raw);  // Risky

    delete raw;  // Double delete when shared_ptr destructs
}

void weakPtrMisuse() {
    std::weak_ptr<int> wp;
    {
        auto sp = std::make_shared<int>(10);
        wp = sp;
    }
    // sp out of scope
    auto locked = wp.lock();  // nullptr but not checked
    std::cout << *locked << std::endl;  // Null pointer dereference
}

int main() {
    DataHolder d1(10);
    DataHolder d2 = d1;  // Shallow copy - double delete

    mixedPointerUsage();
    weakPtrMisuse();

    return 0;
}
