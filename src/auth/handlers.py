from user.models import User
from tornado.escape import json_encode
import random
import string
from conf import settings
import tornado.web
import tornado.auth


def generate_token():
    return ''.join(random.choice(string.ascii_letters) for i in range(20))


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')
        user = User.objects.find(raw_uid="email:%s" % email)

        authenticated = False

        if user:
            authenticated = True
            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)

        self.write(json_encode({'authenticated': authenticated}))


class FacebookGraphLoginHandler(tornado.web.RequestHandler,
                                tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            fb_data = yield self.get_authenticated_user(
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
                client_id=settings.FACEBOOK_APP_ID,
                client_secret=settings.FACEBOOK_APP_SECRET,
                code=self.get_argument("code"))

            # Save the user with e.g. set_secure_cookie
            uid = "facebook:%s" % fb_data['id']
            user = User.objects.find(raw_uid=uid)
            if not user:
                user = User.objects.create_user(
                    uid,
                    fb_data['name'].lower().replace(' ', '_'),
                    fb_data['name'],
                    fb_data['picture']['data']['url'])

            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)
            self.write(json_encode({'authenticated': True}))
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
                client_id=settings.FACEBOOK_APP_ID)
