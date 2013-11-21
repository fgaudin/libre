from tornado.options import define, parse_command_line, options
from index.handlers import IndexHandler
from message.handlers import MessageHandler
from websocket.handlers import WebSocketHandler
from tornado import web, ioloop
from auth.handlers import LoginHandler, FacebookGraphLoginHandler
from user.handlers import UserHandler

define("port", default=8888, help="run on the given port", type=int)


def main():
    parse_command_line()
    app = web.Application(
        [
            (r"/", IndexHandler),
            (r"/login", LoginHandler),
            (r"/fblogin", FacebookGraphLoginHandler),
            (r"/socket", WebSocketHandler),
            (r"/messages", MessageHandler),
            (r"/messages/([0-9]+)", MessageHandler),
            (r"/users/([a-zA-Z0-9_]+)", UserHandler),
            ],
            debug=True,
            static_path='static/',
            cookie_secret='jksjdflksjdfljsdf'
        )
    app.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
