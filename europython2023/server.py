from socket import *
from sock import Sock
from loop import Loop


async def server(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock = Sock(sock)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()

    while True:
        client, addr = await sock.accept()
        print("connected", client, addr)
        loop.create_task(handle_client(client))


async def handle_client(client):
    while True:
        data = await client.recv(100)
        if not data:
            break
        await client.send(b"echo " + data)
    client.close()


server_task = server('', 4588)
loop = Loop()
loop.create_task(server_task)
loop.run()
