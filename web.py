import tornado.ioloop
from tornado import gen
from tornado import web
from tornado import options
from tornado import websocket

from lib.sensoball import SensoBall
import ujson as json


options.define("port", default=6060, type=int, help="Port for the webserver")
options.define("udp-port", default=8326, type=int,
               help="Port for the UDP server")
options.define("board-id", default=None, type=str,
               help="ID of board to connect to")


class DataHandler(websocket.WebSocketHandler):
    default_rate = 60
    default_batch_size = 10
    fields = 'x y z'.split()
    running = False

    @gen.coroutine
    def open(self):
        print("Client connected")
        self.sensoball = self.application.settings['sensoball']

    @gen.coroutine
    def on_message(self, data):
        print("Message from client: ", data)
        message = json.loads(data)
        if message.get('action') == 'start':
            print("Starting data transmission")
            self.rate = message.get('rate', self.default_rate)
            self.batch_size = message.get('rate', self.default_batch_size)
            self.running = True
            yield self._send_data()
        elif message.get('action') == 'resample':
            self.rate = message.get('rate', self.default_rate)
        elif message.get('action') == 'change_batch':
            self.batch_size = message.get('batch_size',
                                          self.default_batch_size)
        elif message.get('action') == 'stop':
            self.running = False

    @gen.coroutine
    def _send_data(self):
        if not self.running:
            return
        samples = self.sensoball.get_samples(
            num_samples=self.batch_size,
            newest=True
        )
        data = [
            {
                'data': dict(zip(self.fields, sample)),
                't': timestamp * 1000,
            } for sample, timestamp in samples
        ]
        yield self.write_message(json.dumps(data))
        tornado.ioloop.IOLoop.instance().call_later(
            1.0 / self.rate,
            self._send_data,
        )

    def on_close(self):
        print("Client disconnected :(")
        self.running = False

    def check_origin(self, origin):
        return True


if __name__ == "__main__":
    options.parse_command_line()
    port = options.options.port
    udp_port = options.options.udp_port
    board_id = options.options.board_id

    ioloop = tornado.ioloop.IOLoop.instance()
    sensoball = SensoBall(
        board_id=board_id,
        ioloop=ioloop,
        port=udp_port,
    )
    sensoball.start()
    app = web.Application(
        [
            (r'/data', DataHandler),
        ],
        template_path="./templates/",
        static_path="./static/",
        debug=True,
        sensoball=sensoball,
    )
    app.listen(port)
    print("Starting server on port:", port)
    ioloop.start()
