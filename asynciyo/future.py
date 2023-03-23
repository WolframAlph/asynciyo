from collections import deque


class ScheduleLater:
    def __init__(self, fut):
        self.fut = fut

    def handle(self, loop, task):
        pass
