from tornado import gen
import tornado.ioloop
import serial
import socket
import time
from collections import deque

from .AsyncUDPServer import UDPStream


def parse_sample(data):
    val = data[1] << 8 | data[0]
    if (val & (1 << (16 - 1))) != 0:
        val = val - (1 << 16)
    return val

_RUN_LOOP = """
sk=net.createConnection(net.UDP,0)
sk:connect(8326,"{hostname}")
tmr.alarm(0, 20, 1, readL3GD20 )
tmr.alarm(1, 100, 1, senddata )
"""


class SensoBall(object):
    def __init__(self, hostip=None, device_path=None, samples_per_frame=3,
                 port=8326, buffer_size=8192, ioloop=None):
        self.device_path = device_path
        self.hostip = hostip
        self.samples_per_frame = samples_per_frame
        self.queue = deque(maxlen=buffer_size)
        self.port = port
        self.ioloop = ioloop or tornado.ioloop.IOLoop.instance()
        if device_path and hostip:
            self._initialize_device()

    def _startserver(self):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.bind(('', self.port))
        self.s = UDPStream(sock, chunk_size=96, in_ioloop=self.ioloop)

    def _stopserver(self):
        self.s.close()

    def start(self):
        self.running = True
        self._startserver()
        self.ioloop.add_callback(self._fill_queue)

    def stop(self):
        self.running = False
        self._stopserver()

    @gen.coroutine
    def _fill_queue(self):
        sample = []
        while self.running:
            data = yield gen.Task(self.s.read_chunk)
            for i in range(0, len(data), 2):
                measurement = parse_sample(data[i:i+2])
                sample.append(measurement)
                if len(sample) == self.samples_per_frame:
                    self.queue.append((tuple(sample), time.time()))
                    sample = sample[:0]

    def _initialize_device(self):
        print("Writing run code")
        device = serial.Serial(self.device_path)
        run_loop = _RUN_LOOP.format(hostname=self.hostip)
        for line in run_loop.split('\n'):
            print(line)
            device.write((line + '\r\n').encode())
            device.readline()
        device.close()

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
