"""In-place heapsort based on a zero-indexed max-heap."""

from __future__ import annotations

from typing import MutableSequence, TypeVar


T = TypeVar("T")


def _sift_down(values: MutableSequence[T], root: int, end: int) -> None:
    """Restore the max-heap property from ``root`` through ``end``."""

    while True:
        left = 2 * root + 1
        if left > end:
            # A node without children already satisfies the heap property.
            return

        right = left + 1
        larger_child = left
        if right <= end and values[right] > values[left]:
            # Heapsort must promote the larger child in a max-heap.
            larger_child = right

        if values[root] >= values[larger_child]:
            # The root dominates both children, so this subtree is a max-heap.
            return

        # Move the larger child upward, then continue where the root moved.
        values[root], values[larger_child] = values[larger_child], values[root]
        root = larger_child


def build_max_heap(values: MutableSequence[T]) -> None:
    """Rearrange ``values`` into a max-heap in O(n) time."""

    # Every index after the last parent is a leaf and needs no heapifying.
    last_parent = (len(values) - 2) // 2
    for root in range(last_parent, -1, -1):
        _sift_down(values, root, len(values) - 1)


def heapsort(values: MutableSequence[T]) -> None:
    """Sort ``values`` in ascending order in place."""

    build_max_heap(values)

    for end in range(len(values) - 1, 0, -1):
        # The root is the largest remaining value, so place it at the end.
        values[0], values[end] = values[end], values[0]

        # Exclude the value just placed and repair the smaller heap.
        _sift_down(values, 0, end - 1)


if __name__ == "__main__":
    sample = [12, 11, 13, 5, 6, 7]
    heapsort(sample)
    print(sample)
