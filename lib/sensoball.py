from tornado import gen
from tornado import iostream
import tornado.ioloop
import struct
import socket
import time
from collections import deque


def parse_sample(data):
    val = data[1] << 8 | data[0]
    if (val & (1 << (16 - 1))) != 0:
        val = val - (1 << 16)
    return val


class SensoBall(object):
    MCAST_GRP = '224.1.2.18'
    MCAST_PORT = 1337

    def __init__(self, board_id=None, samples_per_frame=3,
                 port=8326, buffer_size=8192, ioloop=None):
        self.board_id = board_id
        self.samples_per_frame = samples_per_frame
        self.queue = deque(maxlen=buffer_size)
        self.port = port
        self.ioloop = ioloop or tornado.ioloop.IOLoop.instance()

    def _find_board(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.MCAST_GRP, self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP),
                           socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print("Searching for", (self.board_id or "any board"))
        while True:
            name, (ip, _) = sock.recvfrom(512)
            print("\tFound board {} at {}".format(name.decode(), ip))
            if self.board_id is None or name.decode() == self.board_id:
                return ip

    def _startserver(self):
        #sock = socket.socket(socket.AF_INET,
        #                     socket.SOCK_DGRAM)
        #sock.setblocking(False)
        #sock.bind(('', self.port))
        # self.s = UDPStream(sock, chunk_size=96, in_ioloop=self.ioloop)
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        self.s = iostream.IOStream(sock)
        self.s.connect((self._ip, self.port), callback=self._fill_queue)

    def _stopserver(self):
        self.s.close()

    def start(self):
        self.running = True
        self._ip = self._find_board()
        self._startserver()
        # self.ioloop.add_callback(self._fill_queue)

    def stop(self):
        self.running = False
        self._stopserver()

    @gen.coroutine
    def _fill_queue(self):
        sample = []
        while self.running:
            data = yield self.s.read_bytes(96)
            for i in range(0, len(data), 2):
                measurement = parse_sample(data[i:i+2])
                sample.append(measurement)
                if len(sample) == self.samples_per_frame:
                    self.queue.append((tuple(sample), time.time()))
                    sample = sample[:0]

    def get_samples(self, num_samples=1, newest=False, clear_old=True):
        samples = []
        if self.queue:
            try:
                for i in range(num_samples):
                    if not newest:
                        samples.append(self.queue.pop())
                    else:
                        samples.append(self.queue.popleft())
            except:
                pass
        if clear_old:
            self.queue.clear()
        samples.sort(key=lambda x: x[1])
        return samples
