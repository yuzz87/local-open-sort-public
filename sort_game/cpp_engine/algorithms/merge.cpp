#include "algorithms.h"
#include <vector>

static void mergeRange(std::vector<int>& a, int l, int m, int r, std::vector<int>& tmp) {
    int i = l, j = m + 1, k = l;
    while (i <= m && j <= r) {
        if (a[i] <= a[j]) tmp[k++] = a[i++];
        else tmp[k++] = a[j++];
    }
    while (i <= m) tmp[k++] = a[i++];
    while (j <= r) tmp[k++] = a[j++];
    for (int t = l; t <= r; t++) a[t] = tmp[t];
}

static void mergeSortRec(std::vector<int>& a, int l, int r, std::vector<int>& tmp) {
    if (l >= r) return;
    int m = l + (r - l) / 2;
    mergeSortRec(a, l, m, tmp);
    mergeSortRec(a, m + 1, r, tmp);
    mergeRange(a, l, m, r, tmp);
}

void mergeSort(std::vector<int>& arr) {
    if (arr.size() <= 1) return;
    std::vector<int> tmp(arr.size());
    mergeSortRec(arr, 0, static_cast<int>(arr.size()) - 1, tmp);
}