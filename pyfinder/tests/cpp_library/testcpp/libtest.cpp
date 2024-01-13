#include <iostream>
extern "C" int sum(int *a, int *b);


extern "C" int sum(int *a, int *b) {
    // Test sum with pointers
    return *a + *b;
} 

