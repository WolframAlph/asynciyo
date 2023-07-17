import heapq
import time
from types import coroutine


class _Sleep:
    def __init__(self, delay):
        self.delay = delay

    def handle(self, loop, task):
        heapq.heappush(loop.sleeping, _Sleeping(task, self.delay))


class _Sleeping:
    def __init__(self, task, delay):
        self.task = task
        self.wake_time = time.time() + delay

    @property
    def left(self):
        return max(self.wake_time - time.time(), 0)

    @property
    def ready(self):
        return round(self.left, 3) == 0

    def __gt__(self, other):
        return self.left > other.left

    def __repr__(self):
        return f"Sleeping(ready={self.ready}, left={self.left})"


@coroutine
def sleep(delay):
    yield _Sleep(delay)
