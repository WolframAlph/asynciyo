from .queue import AsyncQueue


class Semaphore:
    def __init__(self, size=None):
        self.__queue = AsyncQueue(maxsize=size)

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()

    async def acquire(self):
        await self.__queue.put(None)

    async def release(self):
        await self.__queue.get()


class Lock(Semaphore):
    def __init__(self):
        super().__init__(size=1)
