from user.models import User
from tornado.escape import json_encode
from conf import settings
import tornado.web
import tornado.auth
from tornado.web import authenticated
from web import BaseHandler
from auth import store_credentials, generate_token, get_identity, email_exists, \
    unsalted_hash
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


class SocialLoginHandler(tornado.web.RequestHandler):
    def authenticate(self, prefix, social_id, username, fullname, pic):
        connection = Redis.get_connection()
        new_user = False
        key = '{0}:{1}'.format(prefix, unsalted_hash(social_id))
        uid = connection.get(key)
        if uid:
            user = User.objects.find(uid=uid.decode())
        else:
            new_user = True
            user = User.objects.create_user(
                username,
                fullname,
                pic)
            connection.set(key, user.uid)

        token = generate_token()
        user.authenticate(token)
        self.set_secure_cookie("auth", token)
        self.render("redirect.html", new_user=new_user)


class FacebookGraphLoginHandler(SocialLoginHandler,
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

            self.authenticate('fb',
                              fb_data['id'],
                              fb_data['name'].lower().replace(' ', '_'),
                              fb_data['name'],
                              fb_data['picture']['data']['url'])
        else:
            yield self.authorize_redirect(
                redirect_uri=settings.FACEBOOK_REDIRECT_URI,
                client_id=settings.FACEBOOK_APP_ID)


class GoogleLoginHandler(SocialLoginHandler,
                         tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            google_data = yield self.get_authenticated_user()

            self.authenticate('gg',
                              google_data['claimed_id'],
                              google_data['name'].lower().replace(' ', '_'),
                              google_data['name'],
                              '')
        else:
            yield self.authenticate_redirect()


class TwitterLoginHandler(SocialLoginHandler,
                          tornado.auth.TwitterMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("oauth_token", None):
            twitter_data = yield self.get_authenticated_user()

            self.authenticate('tw',
                              twitter_data['id_str'],
                              twitter_data['username'],
                              twitter_data['name'],
                              twitter_data['profile_image_url'])
        else:
            yield self.authenticate_redirect()
