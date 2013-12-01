from libre import initApp
from tornado.testing import AsyncHTTPTestCase
from urllib.parse import urlencode
from user.models import User
from tornado.escape import json_decode
from data import Redis


class SignupTest(AsyncHTTPTestCase):
    def setUp(self):
        super(SignupTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

    def tearDown(self):
        super(SignupTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    def get_app(self):
        return initApp()

    def test_signup(self):
        post_data = {'action': 'Signup',
                     'email': 'foo@test.com',
                     'password': 'bar'}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers['location'], '/profile')

        user = User.objects.find(username='foo')
        self.assertIsNotNone(user)

    def test_login_failed_empty(self):
        post_data = {'action': 'Login',
                     'email': '',
                     'password': 'bar'}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(json_decode(response.body)['status'], 'failed')
        self.assertEqual(json_decode(response.body)['error'], 'Email and password are mandatory')

        post_data = {'action': 'Login',
                     'email': 'foo',
                     'password': ''}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(json_decode(response.body)['status'], 'failed')
        self.assertEqual(json_decode(response.body)['error'], 'Email and password are mandatory')

    def test_login_failed(self):
        post_data = {'action': 'Login',
                     'email': 'foo@test.com',
                     'password': 'bar'}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(json_decode(response.body)['status'], 'failed')
        self.assertEqual(json_decode(response.body)['error'], 'Wrong Username/Email and password combination')

    def test_login(self):
        post_data = {'action': 'Signup',
                     'email': 'foo@test.com',
                     'password': 'bar'}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()

        post_data = {'action': 'Login',
                     'email': 'foo@test.com',
                     'password': 'bar'}
        body = urlencode(post_data)
        self.http_client.fetch(self.get_url('/login/email'),
                               self.stop,
                               method='POST',
                               body=body,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers['location'], '/')
