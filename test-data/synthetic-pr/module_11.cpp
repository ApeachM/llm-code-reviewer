#include <iostream>
#include <string.h>

// File: module_11.cpp - BufferManager

class BufferManager {
private:
    char* buf;

public:
    BufferManager(int size) {
        buf = (char*)malloc(size);
    }

    ~BufferManager() {
        delete buf;  // Should use free() with malloc
    }

    void write(const char* data) {
        strcpy(buf, data);
    }
};

void unsafeFunction(char* input) {
    char local[10];
    gets(local);  // Extremely unsafe
    strcpy(local, input);  // No bounds check
}

int main() {
    BufferManager* bm = new BufferManager(100);
    bm->write("Data");
    return 0;
}
