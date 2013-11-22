from user.models import User
from tornado.escape import json_encode
from conf import settings
import tornado.web
import tornado.auth
from tornado.web import authenticated
from web import BaseHandler
from auth import store_credentials, generate_token, get_identity


class SignupHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')
        uid = "email:%s" % email
        user = User.objects.find(raw_uid=uid)

        authenticated = False

        if not user:
            username = email.split('@')[0].lower()
            fullname = email.split('@')[0].replace('.', ' ').replace('_', ' ')
            user = User.objects.create_user(uid, username, fullname)
            store_credentials(user.uid, email, password)
            authenticated = True
            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)

        self.write(json_encode({'authenticated': authenticated}))


class EmailLoginHandler(tornado.web.RequestHandler):
    def post(self):
        authenticated = False
        email = self.get_argument('email')
        password = self.get_argument('password')
        uid = get_identity(email, password)

        if uid:
            user = User.objects.find(uid=uid)
            if user:
                authenticated = True
                token = generate_token()
                user.authenticate(token)
                self.set_secure_cookie("auth", token)

        self.write(json_encode({'authenticated': authenticated}))


class LogoutHandler(BaseHandler):
    @authenticated
    def post(self):
        self.clear_all_cookies()
        self.write(json_encode({'authenticated': False}))


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
            self.render("redirect.html")
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
                client_id=settings.FACEBOOK_APP_ID)


class GoogleLoginHandler(tornado.web.RequestHandler,
                         tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            google_data = yield self.get_authenticated_user()

            uid = "google:{0}".format(google_data['claimed_id'])
            user = User.objects.find(raw_uid=uid)
            if not user:
                user = User.objects.create_user(
                    uid,
                    google_data['name'].lower().replace(' ', '_'),
                    google_data['name'],
                    '')

            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)
            self.render("redirect.html")
        else:
            yield self.authenticate_redirect()
