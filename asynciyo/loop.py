from collections import deque
import heapq
from select import select
from types import coroutine

from typing import List, Set
from .interrupt import *
from .sleep import _Sleeping


class _EventLoop:
    running_loop = None

    def __init__(self, main):
        self.tasks: Set[Task] = set()
        self.sleeping: List[_Sleeping] = []
        self.read_wait = {}
        self.write_wait = {}
        self.ready: deque[Task] = deque()
        self.main = main

    def wake_sleeping_if_ready(self):
        while self.sleeping and (sleeping := self.sleeping[0]).ready:
            self.schedule(sleeping.task)
            heapq.heappop(self.sleeping)

    @coroutine
    def io_poll(self):
        while True:
            timeout = None
            if self.ready:
                timeout = 0
            elif self.sleeping:
                timeout = self.sleeping[0].left

            for r in [f for f in self.read_wait if f.fileno() == -1]:
                self.schedule(self.read_wait.pop(r))

            for w in [f for f in self.write_wait if f.fileno() == -1]:
                self.schedule(self.write_wait.pop(w))

            read, write, _ = select(
                self.read_wait, self.write_wait, [], timeout
            )  # blocking

            for r in read:
                self.schedule(self.read_wait.pop(r))

            for w in write:
                self.schedule(self.write_wait.pop(w))

            self.wake_sleeping_if_ready()
            yield Reschedule()

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
        def raise_io(task):
            if task.exception() is not None:
                raise task.exception()

        main_task = self.create_task(self.main)
        io_task = Task(self.io_poll())
        io_task.add_done_callback(raise_io)
        self.schedule(io_task)

        while not main_task.done():
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


def _close_event_loop():
    global _running_loop
    if _running_loop is None:
        raise Exception("cannot close not running loop")
    _running_loop = None
