# Heap Data Structures Implementation and Analysis

This project implements Heapsort and an array-backed max-priority queue in Python. It also includes a scheduler simulation and a reproducible timing comparison of Heapsort, Quicksort, and Merge Sort.

## Files

- heapsort.py implements bottom-up max-heap construction and in-place Heapsort.
- priority_queue.py implements task insertion, maximum extraction, priority increase, empty checking, and a nonpreemptive scheduler simulation.
- benchmark.py implements the comparison algorithms and measures all three sorts on sorted, reverse-sorted, and random inputs.
- heap_data_structures_report.docx explains the design, complexity, test method, measured results, and scheduler behavior.

## Requirements

- Python 3.11 or later
- No third-party packages

## Run the examples

```bash
python3 heapsort.py
python3 priority_queue.py
```

## Run the benchmark

The default run measures sizes 1,000, 5,000, 10,000, and 20,000. It performs seven repetitions for each algorithm, size, and input distribution, then prints the median time in milliseconds.

```bash
python3 benchmark.py
```

Use smaller values for a quick check:

```bash
python3 benchmark.py --sizes 100 500 1000 --repeats 3
```

## Summary of findings

Heapsort has an O(n log n) running time in its best, average, and worst cases and uses O(1) auxiliary array space. At 20,000 items, its medians ranged from 21.709 to 24.182 milliseconds across the three input distributions. Merge Sort was faster on sorted and reverse-sorted inputs but uses O(n) temporary space. Quicksort was competitive on random input but was slower on ordered inputs in this Python implementation and does not provide Heapsort's worst-case guarantee.

The max-priority queue uses a Python list as a compact binary heap and a dictionary that maps task IDs to heap positions. Insert and maximum extraction take expected amortized O(log n) time in this Python implementation. Priority increase takes expected O(log n) time. These bounds include expected constant-time dictionary access and, for insertion, amortized list growth. The scheduler always selects the highest-priority task that has arrived, with deterministic tie-breaking by arrival time, deadline, and insertion order.

## References

Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.

OpenAI. (2026). Codex [Large language model; assisted with source organization and drafting]. https://openai.com/codex/
