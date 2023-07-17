# Asynchronous HTTPS proxy
import email
import io
import sys
from collections import defaultdict
import socket

import asynciyo as asio


def done(task):
    if (exception := task.exception()) is not None:
        raise exception


async def read_headers(client: asio.asocket):
    buff = io.BytesIO()
    while buff.tell() < 5000:
        try:
            data = await client.read(2000)
            if not data:
                break
            buff.write(data)
            buff.seek(-4, io.SEEK_END)
            if buff.read() == b"\r\n\r\n":
                break
        except IOError:
            break

    try:
        request_text = buff.getvalue().decode()
        request_line, headers_alone = request_text.split('\r\n', 1)
        message = email.message_from_file(io.StringIO(headers_alone))
        return dict(message.items())
    except ValueError:
        return {}


async def copy(dst: asio.asocket, src: asio.asocket, stats, sockno):
    while True:
        try:
            data = await src.read(50000)
            if not data:
                break
            await dst.write(data)
            stats[sockno] += len(data)
        except IOError:
            break
    src.close()
    dst.close()


async def handle_client(queue: asio.AsyncQueue, stats: dict):
    while True:
        client, addr = await queue.get()
        ip, sockno = addr

        headers = await read_headers(client)

        if (host := headers.get("Host")) is None:
            continue

        hostname = host.split(":")[0]
        resource = asio.asocket()

        await resource.connect(hostname, 443)
        await client.write(b"HTTP/1.1 200 OK\r\n\r\n")

        receive = copy(client, resource, stats[ip][hostname], sockno)
        send = copy(resource, client, stats[ip][hostname], sockno)
        await asio.gather(receive, send, raise_exception=True)

        stats[ip][hostname].pop(sockno, None)
        if not stats[ip][hostname]:
            stats[ip].pop(hostname, None)
            if not stats[ip]:
                stats.pop(ip, None)


async def statsd(stats, delay):
    while True:
        lines = set()
        sys.stdout.write("\x1b[2J\x1b[H")
        for ip in stats.keys():
            for hostname in stats[ip].keys():
                for sockno in stats[ip][hostname].keys():
                    lines.add((ip, hostname, sockno, stats[ip][hostname][sockno]))
        for line in lines:
            print(*line)
        await asio.sleep(delay)


async def server(host, port, num_workers=100):
    sock = asio.asocket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()

    queue = asio.AsyncQueue()
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for _ in range(num_workers):
        worker = asio.create_task(handle_client(queue, stats))
        worker.add_done_callback(done)

    statsd_task = asio.create_task(statsd(stats, .5))
    statsd_task.add_done_callback(done)

    while True:
        client, addr = await sock.accept()
        await queue.put((client, addr))


asio.run(server('', 4588))
