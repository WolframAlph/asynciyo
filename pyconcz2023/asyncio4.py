from socket import *
from select import select
from selectors import EVENT_READ, EVENT_WRITE

# ========== USER CODE ==========

def server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    while True:
        yield sock, EVENT_READ
        client, addr = sock.accept()
        print("connected", client)
        tasks.append(handle_client(client))


def handle_client(sock):
    while True:
        yield sock, EVENT_READ
        data = sock.recv(100)
        if not data:
            break
        yield sock, EVENT_WRITE
        sock.send(b"echo " + data)

# ========== USER CODE ==========


# ========== LIBRARY CODE ==========

read_waiting = {}
write_waiting = {}
tasks = [server('', 1234)]

while read_waiting or tasks or write_waiting:
    if not tasks:
        ready_to_read, ready_to_write, _ = select(read_waiting.keys(), write_waiting.keys(), [])
        for sock in ready_to_read:
            tasks.append(read_waiting.pop(sock))
        for sock in ready_to_write:
            tasks.append(write_waiting.pop(sock))

    task = tasks.pop(0)

    try:
        sock, event = next(task)
        if event == EVENT_READ:
            read_waiting[sock] = task
        else:
            write_waiting[sock] = task
    except StopIteration:
        print("task done", task)

# ========== LIBRARY CODE ==========
