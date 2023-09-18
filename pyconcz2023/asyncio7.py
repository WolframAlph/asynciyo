from collections import deque
from select import select
from selectors import EVENT_READ, EVENT_WRITE
from socket import *
from types import coroutine


# ======= LIBRARY CODE =========
class Loop:
    def __init__(self):
        self.tasks = deque()
        self.read_wait = {}
        self.write_wait = {}

    def create_task(self, gen):
        self.tasks.append(Task(gen))

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
                sock, event = task.run()
                if event == EVENT_READ:
                    self.read_wait[sock] = task
                elif event == EVENT_WRITE:
                    self.write_wait[sock] = task
                else:
                    raise Exception("you suck")
            except StopIteration:
                continue


class Sock:
    def __init__(self, sock):
        self.sock = sock

    @coroutine
    def accept(self, *a, **kw):
        yield self.sock, EVENT_READ
        client_sock, addr = self.sock.accept(*a, **kw)
        return Sock(client_sock), addr

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


class Task:
    def __init__(self, gen):
        self.gen = gen

    def run(self):
        return self.gen.send(None)

# ======= LIBRARY CODE =========


# ========== USER CODE ==========

async def server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    sock = Sock(sock)
    while True:
        client, addr = await sock.accept()
        print("connected", client)
        loop.create_task(handle_client(client))


async def handle_client(sock):
    while True:
        data = await sock.recv(100)
        if not data:
            break
        await sock.send(b"echo " + data)


loop = Loop()
loop.create_task(server('', 1234))
loop.run()
# ========== USER CODE ==========

