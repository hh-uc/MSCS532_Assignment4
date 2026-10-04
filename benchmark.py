"""Reproducible timing comparison for Heapsort, Quicksort, and Merge Sort."""

from __future__ import annotations

import argparse
import random
import statistics
import time
from collections.abc import Callable

from heapsort import heapsort


SortFunction = Callable[[list[int]], None]


def quicksort(values: list[int]) -> None:
    """Sort in place with an iterative median-of-three three-way Quicksort."""

    if len(values) < 2:
        return

    stack = [(0, len(values) - 1)]
    while stack:
        low, high = stack.pop()
        while low < high:
            middle = (low + high) // 2
            pivot = sorted((values[low], values[middle], values[high]))[1]

            # Three-way partitioning prevents duplicate keys from degrading badly.
            lower = low
            current = low
            upper = high
            while current <= upper:
                if values[current] < pivot:
                    values[lower], values[current] = values[current], values[lower]
                    lower += 1
                    current += 1
                elif values[current] > pivot:
                    values[current], values[upper] = values[upper], values[current]
                    upper -= 1
                else:
                    current += 1

            left = (low, lower - 1)
            right = (upper + 1, high)

            # Process the smaller side immediately to keep the stack compact.
            if left[1] - left[0] < right[1] - right[0]:
                if right[0] < right[1]:
                    stack.append(right)
                low, high = left
            else:
                if left[0] < left[1]:
                    stack.append(left)
                low, high = right


def merge_sort(values: list[int]) -> None:
    """Sort the supplied list with bottom-up Merge Sort and O(n) temporary space."""

    size = len(values)
    if size < 2:
        return

    source = values
    target = [0] * size
    width = 1

    while width < size:
        for start in range(0, size, 2 * width):
            middle = min(start + width, size)
            end = min(start + 2 * width, size)
            left = start
            right = middle

            for output in range(start, end):
                if right >= end or (left < middle and source[left] <= source[right]):
                    target[output] = source[left]
                    left += 1
                else:
                    target[output] = source[right]
                    right += 1

        source, target = target, source
        width *= 2

    if source is not values:
        values[:] = source


def make_input(size: int, distribution: str, seed: int) -> list[int]:
    """Create one deterministic input for a benchmark case."""

    if distribution == "sorted":
        return list(range(size))
    if distribution == "reverse":
        return list(range(size - 1, -1, -1))
    if distribution == "random":
        generator = random.Random(seed)
        return [generator.randrange(size * 10) for _ in range(size)]
    raise ValueError(f"unknown distribution: {distribution}")


def benchmark(
    sizes: list[int], repeats: int, seed: int
) -> list[tuple[str, int, str, float]]:
    """Return median milliseconds for every algorithm and input case."""

    algorithms: dict[str, SortFunction] = {
        "Heapsort": heapsort,
        "Quicksort": quicksort,
        "Merge Sort": merge_sort,
    }
    results: list[tuple[str, int, str, float]] = []

    for distribution in ("sorted", "reverse", "random"):
        for size in sizes:
            baseline = make_input(size, distribution, seed + size)
            expected = sorted(baseline)

            for name, algorithm in algorithms.items():
                samples: list[float] = []
                for _ in range(repeats):
                    values = baseline.copy()
                    started = time.perf_counter_ns()
                    algorithm(values)
                    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
                    if values != expected:
                        raise AssertionError(f"{name} produced an incorrect result")
                    samples.append(elapsed_ms)

                results.append((distribution, size, name, statistics.median(samples)))

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 5000, 10000, 20000])
    parser.add_argument("--repeats", type=int, default=7)
    parser.add_argument("--seed", type=int, default=532)
    args = parser.parse_args()
    if any(size <= 0 for size in args.sizes):
        parser.error("sizes must be positive")
    if args.repeats <= 0:
        parser.error("repeats must be positive")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    print("distribution,size,algorithm,median_ms")
    for distribution, size, name, median_ms in benchmark(
        arguments.sizes, arguments.repeats, arguments.seed
    ):
        print(f"{distribution},{size},{name},{median_ms:.3f}")
