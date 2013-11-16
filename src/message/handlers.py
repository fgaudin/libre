import tornado.web


class MessageHandler(tornado.web.RequestHandler):
    def post(self):
        self.write("You wrote " + self.get_argument("message"))
