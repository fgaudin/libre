from data import next_id, Redis
from unittest.case import TestCase


class NextIdTest(TestCase):
    def setUp(self):
        connection = Redis.get_connection()
        connection.flushall()

    def tearDown(self):
        connection = Redis.get_connection()
        connection.flushall()

    def test_next_id(self):
        self.assertEqual(next_id('user'), 1)
        self.assertEqual(next_id('user'), 2)
        self.assertEqual(next_id('message'), 1)
