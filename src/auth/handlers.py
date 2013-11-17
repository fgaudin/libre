import tornado.web


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_secure_cookie("auth", '1234')
