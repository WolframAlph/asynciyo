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
    return client


def handle_client(sock):
    data = sock.recv(100)
    if not data:
        sock.close()
    else:
        sock.send(b"echo " + data)


server_sock = server('', 1234)
sockets = [server_sock]


while True:
    ready, _, _ = select(sockets, [], [])
    for socket in ready:
        if socket is server_sock:
            new_client = accept_client(socket)
            sockets.append(new_client)
        else:
            handle_client(socket)
