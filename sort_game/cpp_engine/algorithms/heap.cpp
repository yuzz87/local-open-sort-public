#include "algorithms.h"
#include <algorithm> // std::swap

static void heapify(std::vector<int>& a, int n, int i) {
    int largest = i;
    int l = 2 * i + 1;
    int r = 2 * i + 2;

    if (l < n && a[l] > a[largest]) largest = l;
    if (r < n && a[r] > a[largest]) largest = r;

    if (largest != i) {
        std::swap(a[i], a[largest]);
        heapify(a, n, largest);
    }
}

void heapSort(std::vector<int>& arr) {
    int n = static_cast<int>(arr.size());
    if (n <= 1) return;

    for (int i = n / 2 - 1; i >= 0; i--) heapify(arr, n, i);
    for (int i = n - 1; i > 0; i--) {
        std::swap(arr[0], arr[i]);
        heapify(arr, i, 0);
    }
}