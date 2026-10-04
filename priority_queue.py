"""Array-backed max-priority queue and nonpreemptive scheduler simulation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable


@dataclass(frozen=True)
class Task:
    """A schedulable unit of work."""

    task_id: str
    priority: int
    arrival_time: int
    deadline: int
    duration: int = 1

    def __post_init__(self) -> None:
        if not self.task_id:
            raise ValueError("task_id must not be empty")
        if self.arrival_time < 0:
            raise ValueError("arrival_time must be nonnegative")
        if self.deadline < 0:
            raise ValueError("deadline must be nonnegative")
        if self.duration <= 0:
            raise ValueError("duration must be positive")


@dataclass(frozen=True)
class ScheduleResult:
    """Observed timing for one completed task."""

    task_id: str
    priority: int
    start_time: int
    completion_time: int
    waiting_time: int
    tardiness: int


@dataclass
class _Entry:
    task: Task
    sequence: int


class MaxPriorityQueue:
    """A binary max-heap with expected amortized O(log n) update operations."""

    def __init__(self) -> None:
        self._heap: list[_Entry] = []
        self._positions: dict[str, int] = {}
        self._next_sequence = 0

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        """Return True when the queue contains no tasks."""

        return not self._heap

    @staticmethod
    def _parent(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def _left(index: int) -> int:
        return 2 * index + 1

    def _key(self, entry: _Entry) -> tuple[int, int, int, int]:
        # Higher priority wins. Ties favor earlier arrival, deadline, and insert.
        task = entry.task
        return (
            task.priority,
            -task.arrival_time,
            -task.deadline,
            -entry.sequence,
        )

    def _swap(self, first: int, second: int) -> None:
        self._heap[first], self._heap[second] = self._heap[second], self._heap[first]

        # Expected O(1) map updates avoid an O(n) scan before a key change.
        self._positions[self._heap[first].task.task_id] = first
        self._positions[self._heap[second].task.task_id] = second

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = self._parent(index)
            if self._key(self._heap[parent]) >= self._key(self._heap[index]):
                return
            self._swap(parent, index)
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._heap)
        while True:
            left = self._left(index)
            right = left + 1
            largest = index

            if left < size and self._key(self._heap[left]) > self._key(self._heap[largest]):
                largest = left
            if right < size and self._key(self._heap[right]) > self._key(self._heap[largest]):
                largest = right
            if largest == index:
                return

            self._swap(index, largest)
            index = largest

    def insert(self, task: Task) -> None:
        """Insert ``task`` while preserving the max-heap property."""

        if task.task_id in self._positions:
            raise ValueError(f"duplicate task_id: {task.task_id}")

        entry = _Entry(task=task, sequence=self._next_sequence)
        self._next_sequence += 1
        self._heap.append(entry)
        self._positions[task.task_id] = len(self._heap) - 1

        # A new leaf can violate the heap property only along its ancestor path.
        self._sift_up(len(self._heap) - 1)

    def extract_max(self) -> Task:
        """Remove and return the highest-priority task."""

        if self.is_empty():
            raise IndexError("extract_max from an empty priority queue")

        maximum = self._heap[0].task
        last = self._heap.pop()
        del self._positions[maximum.task_id]

        if self._heap:
            # The last leaf fills the root vacancy before the heap is repaired.
            self._heap[0] = last
            self._positions[last.task.task_id] = 0
            self._sift_down(0)

        return maximum

    def increase_priority(self, task_id: str, new_priority: int) -> None:
        """Increase a task's priority and move it toward the root as needed."""

        if task_id not in self._positions:
            raise KeyError(task_id)

        index = self._positions[task_id]
        current = self._heap[index].task
        if new_priority < current.priority:
            raise ValueError("new priority must not be lower than the current priority")

        self._heap[index].task = replace(current, priority=new_priority)

        # Increasing a max-heap key cannot create a violation below the node.
        self._sift_up(index)


def simulate_scheduler(tasks: Iterable[Task]) -> list[ScheduleResult]:
    """Run a nonpreemptive highest-priority-first scheduler."""

    pending = sorted(tasks, key=lambda task: (task.arrival_time, task.task_id))
    if len({task.task_id for task in pending}) != len(pending):
        raise ValueError("task IDs must be unique")

    queue = MaxPriorityQueue()
    results: list[ScheduleResult] = []
    next_task = 0
    clock = 0

    while next_task < len(pending) or not queue.is_empty():
        while next_task < len(pending) and pending[next_task].arrival_time <= clock:
            # Only arrived tasks are eligible for the current scheduling choice.
            queue.insert(pending[next_task])
            next_task += 1

        if queue.is_empty():
            # When no work is ready, jump directly to the next arrival time.
            clock = pending[next_task].arrival_time
            continue

        task = queue.extract_max()
        start = clock
        clock += task.duration
        results.append(
            ScheduleResult(
                task_id=task.task_id,
                priority=task.priority,
                start_time=start,
                completion_time=clock,
                waiting_time=start - task.arrival_time,
                tardiness=max(0, clock - task.deadline),
            )
        )

    return results


if __name__ == "__main__":
    sample_tasks = [
        Task("A", priority=3, arrival_time=0, deadline=5, duration=2),
        Task("B", priority=5, arrival_time=0, deadline=3, duration=1),
        Task("C", priority=4, arrival_time=1, deadline=5, duration=2),
        Task("D", priority=5, arrival_time=3, deadline=6, duration=1),
    ]
    for result in simulate_scheduler(sample_tasks):
        print(result)
