from gen import a
from typing import Generator


class Task:
    def __init__(self, coro):
        # self.generator = generator
        # self.stack = [self.generator]
        self.coro = coro

    def run(self):
        return self.coro.send(None)
        # current = self.stack.pop()
        # value = None
        # while True:
        #     try:
        #         yielded = current.send(value)
        #         self.stack.append(current)
        #         if isinstance(yielded, Generator):
        #             current = yielded
        #         else:
        #             return yielded
        #         value = None
        #     except StopIteration as e:
        #         if not self.stack:
        #             raise
        #         current = self.stack.pop()
        #         value = e.value


task = Task(a())
