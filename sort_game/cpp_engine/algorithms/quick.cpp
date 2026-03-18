#include "algorithms.h"
#include <algorithm> // std::swap

static int partitionRange(std::vector<int>& a, int low, int high) {
    int pivot = a[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (a[j] < pivot) {
            i++;
            std::swap(a[i], a[j]);
        }
    }
    std::swap(a[i + 1], a[high]);
    return i + 1;
}

static void quickSortRec(std::vector<int>& a, int low, int high) {
    if (low >= high) return;
    int p = partitionRange(a, low, high);
    quickSortRec(a, low, p - 1);
    quickSortRec(a, p + 1, high);
}

void quickSort(std::vector<int>& arr) {
    if (arr.size() <= 1) return;
    quickSortRec(arr, 0, static_cast<int>(arr.size()) - 1);
}