from tornado.testing import AsyncTestCase
from data import Redis


class MessageTest(AsyncTestCase):
    def setUp(self):
        connection = Redis.get_connection()
        connection.flushall()

    def tearDown(self):
        connection = Redis.get_connection()
        connection.flushall()

    def test_create_message(self):
        pass
