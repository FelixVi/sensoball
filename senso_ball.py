import sys
import serial
import socket
import multiprocessing


def parse_sample(data):
    val = data[1] << 8 | data[0]
    if (val & (1 << (16 - 1))) != 0:
        val = val - (1 << 16)
    return val


class SensoBall(object):
    def __init__(self, device_path, num_samples=3):
        self.num_samples = num_samples
        self.queue = multiprocessing.Queue()
        self.sensoballdata = SensoBallData(device_path, self.queue)
        self.datathread = multiprocessing.Process(target=self.sensoballdata.run)
        self.datathread.start()

    def __iter__(self):
        while True:
            data = [self.queue.get() for _ in range(self.num_samples)]
            yield data


class SensoBallData(object):
    run_loop = """
sk=net.createConnection(net.UDP,0)\r\n
sk:connect(8326,"{hostname}")\r\n
tmr.alarm(1, 100, 1, senddata )\r\n
tmr.alarm(0, 20, 1, readL3GD20 )\r\n
"""

    def __init__(self, device_path, queue):
        self.queue = queue
        self.device_path = device_path

    def run(self):
        self.UDP_PORT = 8326
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)
        self.sock.bind(('', 8326))

        hostname = '10.0.0.129'  # socket.gethostbyname(socket.gethostname())
        # device = serial.Serial(self.device_path)

        # run_loop = self.run_loop.format(hostname=hostname)
        # device.write(run_loop.encode())
        while True:
            data = self.sock.recv(96)
            i = 0
            while True:
                try:
                    sample = parse_sample(data[i:i+2])
                    self.queue.put(sample)
                except IndexError:
                    break
                i += 2


if __name__ == "__main__":
    device_path = sys.argv[1]
    sensoball = SensoBall(device_path)
    for sample in iter(sensoball):
        print(sample)

