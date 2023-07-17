from collections import deque
import heapq
from select import select

from typing import List
from .sleep import _Sleeping
from .task import Task


class _EventLoop:

    def __init__(self, main):
        self.sleeping: List[_Sleeping] = []
        self.read_wait = {}
        self.write_wait = {}
        self.ready: deque[Task] = deque()
        self.main = main

    def io_poll(self):
        timeout = None
        if self.ready:
            timeout = 0
        elif self.sleeping:
            timeout = self.sleeping[0].left
            # print(timeout)

        for r in [f for f in self.read_wait if f.fileno() == -1]:
            self.schedule(self.read_wait.pop(r))

        for w in [f for f in self.write_wait if f.fileno() == -1]:
            self.schedule(self.write_wait.pop(w))

        read, write, _ = select(self.read_wait, self.write_wait, [], timeout)  # blocking

        for r in read:
            self.schedule(self.read_wait.pop(r))

        for w in write:
            self.schedule(self.write_wait.pop(w))

        # if not read and not write and timeout:
        #     assert self.sleeping[0].ready, timeout

        while self.sleeping and (sleeping := self.sleeping[0]).ready:
            self.schedule(sleeping.task)
            heapq.heappop(self.sleeping)

        if len(self.ready) == 0:
            print(timeout, len(read), len(write), len(self.read_wait), len(self.write_wait), self.sleeping)

    def create_task(self, coro):
        task = Task(coro)
        self.run_once(task)
        return task

    def run_once(self, task):
        try:
            interrupt = task.run()
            interrupt.handle(self, task)
        except StopIteration:
            return

    def schedule(self, task: Task):
        self.ready.append(task)

    def get_next_task(self) -> Task:
        return self.ready.popleft()

    def run(self):
        main_task = self.create_task(self.main)

        while not main_task.done():
            self.io_poll()
            task = self.get_next_task()
            self.run_once(task)

        if (exception := main_task.exception()) is not None:
            raise exception
        return main_task.result()


_running_loop = None


def _create_event_loop(main):
    global _running_loop
    if _running_loop is not None:
        raise Exception("cannot create another loop")
    _running_loop = _EventLoop(main)
    return _running_loop


def _get_event_loop():
    if _running_loop is None:
        raise Exception("no running loop")
    return _running_loop
