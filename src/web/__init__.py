from tornado.web import RequestHandler
from auth.models import User


class BaseHandler(RequestHandler):
    def get_current_user(self):
        token = self.get_secure_cookie("auth")
        return User.objects.find(token)
