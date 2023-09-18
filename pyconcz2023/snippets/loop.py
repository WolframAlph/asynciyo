from collections import deque
from select import select
from selectors import EVENT_READ, EVENT_WRITE


class Loop:
    def __init__(self):
        self.tasks = deque()
        self.read_wait = {}
        self.write_wait = {}

    def create_task(self, gen):
        self.tasks.append(gen)

    def run(self):
        while self.tasks or self.read_wait or self.write_wait:
            if not self.tasks:
                read_ready, write_ready, _ = select(self.read_wait.keys(), self.write_wait.keys(), [])
                for sock in read_ready:
                    self.tasks.append(self.read_wait.pop(sock))
                for sock in write_ready:
                    self.tasks.append(self.write_wait.pop(sock))
            task = self.tasks.popleft()
            try:
                sock, event = next(task)
                if event == EVENT_READ:
                    self.read_wait[sock] = task
                elif event == EVENT_WRITE:
                    self.write_wait[sock] = task
                else:
                    raise Exception("you suck")
            except StopIteration:
                continue
