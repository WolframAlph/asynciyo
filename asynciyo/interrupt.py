from .task import Task


class Trap:
    def handle(self, loop: "EventLoop", task: Task):
        pass


class Reschedule(Trap):
    def handle(self, loop: "EventLoop", task: Task):
        loop.schedule(task)
