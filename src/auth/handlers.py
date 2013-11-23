from user.models import User
from tornado.escape import json_encode
from conf import settings
import tornado.web
import tornado.auth
from tornado.web import authenticated
from web import BaseHandler
from auth import store_credentials, generate_token, get_identity, email_exists
from data import Redis


class EmailLoginHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email')
        password = self.get_argument('password')
        action = self.get_argument('action')

        if action == 'Login':
            uid = get_identity(email, password)

            if uid:
                user = User.objects.find(uid=uid)
                if user:
                    token = generate_token()
                    user.authenticate(token)
                    self.set_secure_cookie("auth", token)
                    self.redirect('/')
        elif action == 'Signup':
            already_exists = email_exists(email)

            if not already_exists:
                username = email.split('@')[0].lower()
                fullname = email.split('@')[0].replace('.', ' ').replace('_', ' ')
                user = User.objects.create_user(username, fullname)
                store_credentials(user.uid, email, password)
                token = generate_token()
                user.authenticate(token)
                self.set_secure_cookie("auth", token)
                self.redirect('/profile')


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

            connection = Redis.get_connection()
            new_user = False
            if not connection.exists('fb:{0}'.format(fb_data['id'])):
                new_user = True
                user = User.objects.create_user(
                    fb_data['name'].lower().replace(' ', '_'),
                    fb_data['name'],
                    fb_data['picture']['data']['url'])
                connection.set('fb:{0}'.format(fb_data['id']), user.uid)

            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)
            self.render("redirect.html", new_user=new_user)
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

            connection = Redis.get_connection()
            new_user = False
            if not connection.exists('gg:{0}'.format(google_data['claimed_id'])):
                new_user = True
                user = User.objects.create_user(
                    google_data['name'].lower().replace(' ', '_'),
                    google_data['name'],
                    '')
                connection.set('gg:{0}'.format(google_data['claimed_id']), user.uid)

            token = generate_token()
            user.authenticate(token)
            self.set_secure_cookie("auth", token)
            self.render("redirect.html", new_user=new_user)
        else:
            yield self.authenticate_redirect()
