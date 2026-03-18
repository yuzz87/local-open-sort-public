#include "algorithms.h"

void insertionSort(std::vector<int>& arr) {
    const int n = static_cast<int>(arr.size());
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}