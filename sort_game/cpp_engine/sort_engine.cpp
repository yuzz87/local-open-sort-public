#include <algorithm>
#include <chrono>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "algorithms/algorithms.h"

namespace
{

    constexpr int kMinSize = 100;
    constexpr int kMaxSize = 10000;

    bool tryParseInt(const char *value, int &out)
    {
        try
        {
            out = std::stoi(value);
            return true;
        }
        catch (const std::invalid_argument &)
        {
            return false;
        }
        catch (const std::out_of_range &)
        {
            return false;
        }
    }

    bool isSupportedAlgorithm(const std::string &algorithm)
    {
        return algorithm == "bubble" ||
               algorithm == "selection" ||
               algorithm == "insertion" ||
               algorithm == "merge" ||
               algorithm == "quick" ||
               algorithm == "heap";
    }

    std::vector<int> createShuffledArray(int size, bool hasSeed, unsigned int seed)
    {
        std::vector<int> values(size);

        for (int i = 0; i < size; ++i)
        {
            values[i] = i + 1;
        }

        std::mt19937 rng;
        if (hasSeed)
        {
            rng.seed(seed);
        }
        else
        {
            std::random_device rd;
            rng.seed(rd());
        }

        std::shuffle(values.begin(), values.end(), rng);
        return values;
    }

    void executeSort(const std::string &algorithm, std::vector<int> &values)
    {
        if (algorithm == "bubble")
        {
            bubbleSort(values);
            return;
        }
        if (algorithm == "selection")
        {
            selectionSort(values);
            return;
        }
        if (algorithm == "insertion")
        {
            insertionSort(values);
            return;
        }
        if (algorithm == "merge")
        {
            mergeSort(values);
            return;
        }
        if (algorithm == "quick")
        {
            quickSort(values);
            return;
        }
        if (algorithm == "heap")
        {
            heapSort(values);
            return;
        }
    }

} // namespace

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        std::cerr << "Usage: sort_engine <algorithm> <size> [seed]\n";
        return 2;
    }

    const std::string algorithm = argv[1];
    if (!isSupportedAlgorithm(algorithm))
    {
        std::cerr << "Unknown algorithm\n";
        return 2;
    }

    int size = 0;
    if (!tryParseInt(argv[2], size) || size < kMinSize || size > kMaxSize)
    {
        std::cerr << "Invalid size\n";
        return 2;
    }

    bool hasSeed = false;
    unsigned int seed = 0;

    if (argc >= 4)
    {
        int parsedSeed = 0;
        if (!tryParseInt(argv[3], parsedSeed) || parsedSeed < 0)
        {
            std::cerr << "Invalid seed\n";
            return 2;
        }

        hasSeed = true;
        seed = static_cast<unsigned int>(parsedSeed);
    }

    std::vector<int> values = createShuffledArray(size, hasSeed, seed);

    const auto start = std::chrono::high_resolution_clock::now();
    executeSort(algorithm, values);
    const auto end = std::chrono::high_resolution_clock::now();

    const double durationMs =
        std::chrono::duration<double, std::milli>(end - start).count();

    std::cout << "{";
    std::cout << "\"algorithm\":\"" << algorithm << "\",";
    std::cout << "\"size\":" << size << ",";
    if (hasSeed)
    {
        std::cout << "\"seed\":" << seed << ",";
    }
    else
    {
        std::cout << "\"seed\":null,";
    }
    std::cout << "\"duration_ms\":" << durationMs;
    std::cout << "}\n";

    return 0;
}