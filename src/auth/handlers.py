import tornado.web
from auth.models import User


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        user = User.objects.find(uid='a672116e8e437feec5499d4ef4b5d2608ee6beb7f31e81f5e8fb45fd')
        token = '1234'
        user.authenticate(token)
        self.set_secure_cookie("auth", token)
