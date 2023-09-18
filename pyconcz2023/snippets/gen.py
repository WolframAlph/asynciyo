from typing import Generator


def a():
    bret = yield b()
    print(bret)
    dret = yield d()
    print(dret)


def b():
    yield c()
    return "b is done"


def c():
    yield 1
    yield 2
    yield 3


def d():
    yield 4
    yield 5
    return "d is done"


class Task:
    def __init__(self, gen):
        self.gen = gen
        self.stack = [gen]

    def run(self):
        # iterative DFS
        current = self.stack.pop()
        value = None
        while True:
            try:
                yielded = current.send(value)
                self.stack.append(current)
                if isinstance(yielded, Generator):
                    current = yielded
                else:
                    return yielded
                value = None
            except StopIteration as e:
                if not self.stack:
                    raise
                current = self.stack.pop()
                value = e.value


task = Task(a())
