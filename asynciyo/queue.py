from collections import deque

from .task import Future, Task


class AsyncQueue:
    def __init__(self, maxsize: int = None):
        self.__queue: deque[Task] = deque()
        self.__wait_get: deque[Future] = deque()
        self.__wait_put: deque[Future] = deque()
        self.__maxsize: int = maxsize if maxsize is not None and maxsize > 0 else None
        from . import _get_event_loop
        self.__loop = _get_event_loop()

    def empty(self) -> bool:
        return not self.__queue

    def full(self) -> bool:
        if self.__maxsize is None:
            return False
        return len(self.__queue) >= self.__maxsize

    @staticmethod
    def __wakeup_next_waiter(waiters):
        if not waiters:
            return
        waiter = waiters.popleft()
        waiter.set_result(None)

    def __get(self):
        return self.__queue.popleft()

    def __put(self, item):
        self.__queue.append(item)

    def __put_nowait(self, item):
        if self.full():
            raise Exception("queue is full")
        self.__put(item)
        self.__wakeup_next_waiter(self.__wait_get)

    def __get_nowait(self):
        if self.empty():
            raise Exception("queue is empty")
        item = self.__get()
        self.__wakeup_next_waiter(self.__wait_put)
        return item

    async def put(self, item):
        while self.full():
            fut = Future()
            self.__wait_put.append(fut)
            await fut
        self.__put_nowait(item)

    async def get(self):
        while self.empty():
            fut = Future()
            self.__wait_get.append(fut)
            await fut
        return self.__get_nowait()
