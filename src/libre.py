from tornado.options import define, parse_command_line, options
from index.handlers import IndexHandler
from message.handlers import MessageHandler, LikeHandler
from websocket.handlers import WebSocketHandler
from tornado import web, ioloop
from auth.handlers import FacebookGraphLoginHandler, \
    LogoutHandler, EmailLoginHandler, GoogleLoginHandler, TwitterLoginHandler
from user.handlers import UserHandler, ProfileHandler
from conf import settings
from comment.handlers import CommentHandler
from notification.handlers import NotificationHandler
from button.handlers import ButtonHandler

define("port", default=8888, help="run on the given port", type=int)


def main():
    parse_command_line()
    app = web.Application(
        [
            (r"/", IndexHandler),
            (r"/profile", ProfileHandler),
            (r"/logout", LogoutHandler),
            (r"/login/email", EmailLoginHandler),
            (r"/login/facebook", FacebookGraphLoginHandler),
            (r"/login/google", GoogleLoginHandler),
            (r"/login/twitter", TwitterLoginHandler),
            (r"/notifications", NotificationHandler),
            (r"/socket", WebSocketHandler),
            (r"/messages", MessageHandler),
            (r"/messages/([0-9]+)", MessageHandler),
            (r"/like", LikeHandler),
            (r"/comments", CommentHandler),
            (r"/users/([a-zA-Z0-9_]+)", UserHandler),
            (r"/button", ButtonHandler),
            ],
            debug=True,
            static_path='static/',
            cookie_secret=settings.SECRET_KEY,
            twitter_consumer_key=settings.TWITTER_CONSUMER_KEY,
            twitter_consumer_secret=settings.TWITTER_CONSUMER_SECRET
        )
    app.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
