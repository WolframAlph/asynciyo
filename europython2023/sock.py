from selectors import EVENT_WRITE, EVENT_READ
from types import coroutine


class Sock:
    def __init__(self, sock):
        self.sock = sock

    @coroutine
    def accept(self, *a, **kw):
        yield self.sock, EVENT_READ
        client, addr = self.sock.accept(*a, **kw)
        return Sock(client), addr

    @coroutine
    def recv(self, *a, **kw):
        yield self.sock, EVENT_READ
        data = self.sock.recv(*a, **kw)
        return data

    @coroutine
    def send(self, *a, **kw):
        yield self.sock, EVENT_WRITE
        return self.sock.send(*a, **kw)

    def __getattr__(self, item):
        return getattr(self.sock, item)

