from tornado.testing import AsyncTestCase
from data import next_id


class NextIdTest(AsyncTestCase):
    def test_next_id(self):
        self.assertEqual(next_id('user'), 1)
        self.assertEqual(next_id('user'), 2)
        self.assertEqual(next_id('message'), 1)
