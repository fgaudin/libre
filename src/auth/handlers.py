import tornado.web
from user.models import User
from tornado.escape import json_encode
import random
import string


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')
        user = User.objects.find(raw_uid="email:%s" % email)

        authenticated = False

        if user:
            authenticated = True
            token = ''.join(random.choice(string.ascii_letters) for i in range(20))
            user.authenticate(token)
            self.set_secure_cookie("auth", token)

        self.write(json_encode({'authenticated': authenticated}))
