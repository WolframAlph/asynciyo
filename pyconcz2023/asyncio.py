from socket import *


host = ''
port = 1234
sock = socket(AF_INET, SOCK_STREAM)
sock.bind((host, port))
sock.listen()

while True:
    client, addr = sock.accept()
    print("connected", client)
    while True:
        data = client.recv(100)
        if not data:
            break
        client.send(b"echo " + data)
