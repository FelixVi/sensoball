from tornado import ioloop
from tornado import gen
from tornado import web
from tornado import websocket

from senso_ball import SensoBall
import ujson as json


class DataHandler(websocket.WebSocketHandler):
    @gen.coroutine
    def open(self):
        print("Client connected")
        sensoball = self.application.settings['sensoball']
        fields = 'x y z'.split()
        for i, sample in enumerate(iter(sensoball)):
            if i % 10 == 0:
                data = dict(zip(fields, sample))
                yield self.write_message(json.dumps(data))

    def on_message(self, data):
        print("Message from client: ", data)

    def on_close(self):
        print("Client disconnected :(")


if __name__ == "__main__":
    sensoball = SensoBall('/dev/ttyUSB1')
    app = web.Application(
        [
            (r'/data', DataHandler),
        ],
        template_path="./templates/",
        static_path="./static/",
        debug=True,
        sensoball=sensoball,
    )
    app.listen(8081)
    ioloop.IOLoop.current().start()
