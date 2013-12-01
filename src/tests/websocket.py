from libre import initApp
from tornado.testing import AsyncHTTPTestCase, gen_test, IOLoop
from data import Redis
from tornado.websocket import websocket_connect, WebSocketClientConnection
from user.models import User
from auth import generate_token
from tornado.web import create_signed_value
from tornado import httpclient
from tornado.escape import json_encode, json_decode


class WebsocketTest(AsyncHTTPTestCase):
    def setUp(self):
        super(WebsocketTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

    def tearDown(self):
        super(WebsocketTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    def get_app(self):
        return initApp()

    def get_protocol(self):
        return 'ws'

    @gen_test
    def test_websocket_unauthenticated(self):
        socket = yield websocket_connect(self.get_url('/socket'))
        message = yield socket.read_message()
        self.assertIsNone(message)

    @gen_test
    def test_websocket(self):
        user = User.objects.create('foo',
                                   'John Doe',
                                   'http://test.com/img.jpg')
        token = generate_token()
        user.authenticate(token)

        cookie_value = create_signed_value(self.get_app().settings["cookie_secret"],
                                     'auth', token)

        request = httpclient.HTTPRequest(self.get_url('/socket'))
        request.headers['Cookie'] = 'auth="{0}"'.format(cookie_value.decode())
        request = httpclient._RequestProxy(
                      request, httpclient.HTTPRequest._DEFAULTS)

        socket = yield WebSocketClientConnection(IOLoop.current(), request).connect_future
        socket.write_message(json_encode({'type': 'search', 'term': 'test'}))
        message = yield socket.read_message()
        self.assertEqual(json_decode(message), {"data": [], "type": "user"})
