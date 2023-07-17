from collections import deque

from .task import Future, Task


class AsyncQueue:
    def __init__(self, maxsize: int = None):
        self._queue: deque[Task] = deque()
        self._wait_get: deque[Future] = deque()
        self._wait_put: deque[Future] = deque()
        self._maxsize: int = maxsize if maxsize is not None and maxsize > 0 else None
        from . import _get_event_loop
        self._loop = _get_event_loop()

    def empty(self) -> bool:
        return not self._queue

    def full(self) -> bool:
        if self._maxsize is None:
            return False
        return len(self._queue) >= self._maxsize

    @staticmethod
    def _wakeup_next_waiter(waiters):
        if not waiters:
            return
        waiter = waiters.popleft()
        waiter.set_result(None)

    def _get(self):
        return self._queue.popleft()

    def _put(self, item):
        self._queue.append(item)

    def _put_nowait(self, item):
        if self.full():
            raise Exception("queue is full")
        self._put(item)
        self._wakeup_next_waiter(self._wait_get)

    def _get_nowait(self):
        if self.empty():
            raise Exception("queue is empty")
        item = self._get()
        self._wakeup_next_waiter(self._wait_put)
        return item

    async def put(self, item):
        while self.full():
            fut = Future()
            self._wait_put.append(fut)
            await fut
        self._put_nowait(item)

    async def get(self):
        while self.empty():
            fut = Future()
            self._wait_get.append(fut)
            await fut
        return self._get_nowait()
