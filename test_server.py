from tornado import gen
from tornado import ioloop

from lib.AsyncUDPServer import UDPStream
import socket

@gen.coroutine
def read_socket(s):
    while True:
        data = yield gen.Task(s.read_chunk)
        print(data)
        print(len(data))

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)
sock.setblocking(False)
print("binding")
sock.bind(('', 8326))
s = UDPStream(sock, chunk_size=96)

print("starting loop")
ioloop.IOLoop.instance().add_callback(read_socket, s)
ioloop.IOLoop.instance().start()

