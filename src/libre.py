from tornado.options import define, parse_command_line, options
from index.handlers import IndexHandler
from message.handlers import MessageHandler
from websocket.handlers import WebSocketHandler
from tornado import web, ioloop

define("port", default=8888, help="run on the given port", type=int)


def main():
    parse_command_line()
    app = web.Application(
        [
            (r"/", IndexHandler),
            (r"/socket/", WebSocketHandler),
            (r"/message/create/", MessageHandler),
            ],
            debug=True,
            static_path='static/'
        )
    app.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
