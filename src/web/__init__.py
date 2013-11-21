from tornado.web import RequestHandler
from user.models import User


class BaseHandler(RequestHandler):
    def get_current_user(self):
        token = self.get_secure_cookie("auth")
        if token:
            return User.objects.find(token.decode())
        return None
