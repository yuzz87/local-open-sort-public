#include "algorithms.h"
#include <algorithm> // std::swap

void selectionSort(std::vector<int>& arr) {
    const int n = static_cast<int>(arr.size());
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIdx]) minIdx = j;
        }
        if (minIdx != i) std::swap(arr[i], arr[minIdx]);
    }
}