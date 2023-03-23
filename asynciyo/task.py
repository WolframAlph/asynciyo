from __future__ import annotations
from collections import deque


class WaitFuture:
    def __init__(self, waiters):
        self.__waiters = waiters

    def handle(self, loop, task):
        self.__waiters.append(task)


class Future:
    def __init__(self):
        from .loop import _get_event_loop
        self.__loop = _get_event_loop()
        self.__done = False
        self._result = None
        self._exception = None
        self.__canceled = False
        self.__callbacks: set[callable] = {self.__schedule_waiters}
        self.__waiters = deque()

    def add_done_callback(self, callback):
        self.__callbacks.add(callback)

    def remove_done_callback(self, callback):
        self.__callbacks.discard(callback)

    def __schedule_waiters(self, _):
        while self.__waiters:
            self.__loop.schedule(self.__waiters.popleft())

    def __run_callbacks(self):
        for callback in self.__callbacks:
            callback(self)

    def __finish(self):
        self.__done = True
        self.__run_callbacks()

    def done(self):
        return self.__done

    def exception(self):
        if not self.done():
            raise Exception("exception is not set")
        return self._exception

    def set_exception(self, exception):
        self._exception = exception
        self.__finish()

    def result(self):
        if not self.done():
            raise Exception("result not set")
        return self._result

    def set_result(self, result):
        self._result = result
        self.__finish()

    def __await__(self):
        while True:
            if self.done():
                if (exception := self.exception()) is not None:
                    raise exception
                return self.result()
            yield WaitFuture(self.__waiters)


class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self.__coro = coro

    def set_result(self, result):
        raise Exception("cannot set task result")

    def set_exception(self, exception):
        raise Exception("cannot set task exception")

    def run(self):
        try:
            return self.__coro.send(None)
        except Exception as e:
            if isinstance(e, StopIteration):
                super().set_result(e.value)
            else:
                super().set_exception(e)
            raise StopIteration

    def __repr__(self):
        return (
            f"<Task({'finished' if self.done() else 'pending'}, "
            f"coro={self.__coro}, result={self._result}, exception={self._exception})>"
        )
