import socket
from types import coroutine


class ReadWait:
    def __init__(self, sock):
        self.sock = sock

    def handle(self, loop, task):
        loop.read_wait[self.sock] = task


class WriteWait:
    def __init__(self, sock):
        self.sock = sock

    def handle(self, loop, task):
        loop.write_wait[self.sock] = task


class asocket:
    def __init__(self, sock=None):
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)

    def __getattr__(self, item):
        return getattr(self.sock, item)

    @coroutine
    def accept(self):
        yield ReadWait(self.sock)
        client, addr = self.sock.accept()
        return asocket(sock=client), addr

    @coroutine
    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
        except BlockingIOError:
            yield WriteWait(self.sock)

    @coroutine
    def read(self, n):
        yield ReadWait(self.sock)
        return self.sock.recv(n)

    @coroutine
    def write(self, data: bytes):
        n = 0
        while n < len(data):
            yield WriteWait(self.sock)
            n += self.sock.send(data)
        return n
