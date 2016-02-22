import serial
import time
import sys


def write_init(dev, lua):
    print("Writing init file")
    dev.write(b'file.open("init.lua", "w+")\r\n')
    print(dev.readline())
    lineno = 0
    for line in lua:
        if not line.strip():
            continue
        lineno += 1
        dev.write("file.writeline('{}')\r\n".format(
            line.strip().replace("'", "\'")
        ).encode())
        print(lineno, dev.readline())
        time.sleep(0.1)
    dev.write(b'file.close()\r\n')
    print(dev.readline())
    print("Restarting")
    dev.write(b'node.restart()\r\n')
    print(dev.readline())


if __name__ == "__main__":
    device_path = sys.argv[1]
    init = sys.argv[2]
    device = serial.Serial(device_path)
    write_init(device, open(init))
