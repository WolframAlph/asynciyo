from socket import *
from select import select


"""Select based scheduler"""


def server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    return sock


def accept_client(sock):
    client, addr = sock.accept()
    print("connected", client)
    callbacks[client] = handle_client


def handle_client(sock):
    data = sock.recv(100)
    if not data:
        sock.close()
    else:
        sock.send(b"echo " + data)

def another(sock):
    data2 = sock.recv(100)
    ...
    data3 = sock.recv(100)
    ...


server_sock = server('', 1234)
callbacks = {server_sock: accept_client}


while True:
    ready, _, _ = select(callbacks.keys(), [], [])
    for socket in ready:
        callback = callbacks[socket]
        callback(socket)
