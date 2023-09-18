from socket import *


def server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
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
