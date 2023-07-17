from __future__ import annotations
from collections import deque


class WaitFuture:
    def __init__(self, waiters):
        self._waiters = waiters

    def handle(self, loop, task):
        self._waiters.append(task)


class Future:
    def __init__(self):
        from .loop import _get_event_loop
        self._loop = _get_event_loop()
        self._done = False
        self._result = None
        self._exception = None
        self._callbacks: set[callable] = {self._schedule_waiters}
        self._waiters = deque()

    def add_done_callback(self, callback):
        self._callbacks.add(callback)

    def remove_done_callback(self, callback):
        self._callbacks.discard(callback)

    def _schedule_waiters(self, _):
        while self._waiters:
            self._loop.schedule(self._waiters.popleft())

    def _run_callbacks(self):
        for callback in self._callbacks:
            callback(self)

    def _finish(self):
        self._done = True
        self._run_callbacks()

    def done(self):
        return self._done

    def exception(self):
        if not self.done():
            raise Exception("exception is not set")
        return self._exception

    def set_exception(self, exception):
        self._exception = exception
        self._finish()

    def result(self):
        if not self.done():
            raise Exception("result not set")
        return self._result

    def set_result(self, result):
        self._result = result
        self._finish()

    def __await__(self):
        while True:
            if self.done():
                if (exception := self.exception()) is not None:
                    raise exception
                return self.result()
            yield WaitFuture(self._waiters)


class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self._coro = coro

    def set_result(self, result):
        raise Exception("cannot set task result")

    def set_exception(self, exception):
        raise Exception("cannot set task exception")

    def run(self):
        try:
            return self._coro.send(None)
        except Exception as e:
            if isinstance(e, StopIteration):
                super().set_result(e.value)
            else:
                super().set_exception(e)
            raise StopIteration

    def __repr__(self):
        return (
            f"<Task({'finished' if self.done() else 'pending'}, "
            f"coro={self._coro}, result={self._result}, exception={self._exception})>"
        )
