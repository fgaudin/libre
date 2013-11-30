from tornado.testing import AsyncTestCase
from data import Redis
from user.models import User


class UserTest(AsyncTestCase):
    def setUp(self):
        connection = Redis.get_connection()
        connection.flushall()

    def tearDown(self):
        connection = Redis.get_connection()
        connection.flushall()

    def test_create_user(self):
        user = User.objects.create_user('foo',
                                        'John Doe',
                                        'http://test.com/img.jpg')

        self.assertEqual(user.uid, 1)
        result = User.objects.find(uid=user.uid)
        self.assertEqual(user.uid, result.uid)

    def test_find_user_by_username(self):
        user = User.objects.create_user('foo',
                                        'John Doe',
                                        'http://test.com/img.jpg')

        result = User.objects.find(username=user.username)
        self.assertEqual(user.uid, result.uid)


class FriendShipTest(AsyncTestCase):
    def setUp(self):
        connection = Redis.get_connection()
        connection.flushall()

        self.user1 = User.objects.create_user('foo',
                                              'John Doe',
                                              'http://test.com/img.jpg')

        self.user2 = User.objects.create_user('foo2',
                                              'John Doe2',
                                              'http://test.com/img.jpg')

    def tearDown(self):
        connection = Redis.get_connection()
        connection.flushall()

    def test_request(self):
        self.user1.send_request_to(self.user2)
        self.assertFalse(self.user1.is_friend(self.user2))
        self.assertFalse(self.user2.is_friend(self.user1))
        self.assertTrue(self.user2.is_requested_by(self.user1))
        self.assertFalse(self.user1.is_requested_by(self.user2))

    def test_accept(self):
        self.user1.send_request_to(self.user2)
        self.user2.accept_request_from(self.user1)
        self.assertTrue(self.user1.is_friend(self.user2))
        self.assertTrue(self.user2.is_friend(self.user1))
        self.assertFalse(self.user2.is_requested_by(self.user1))
        self.assertFalse(self.user1.is_requested_by(self.user2))

    def test_cancel(self):
        self.user1.send_request_to(self.user2)
        self.user1.cancel_request_to(self.user2)
        self.assertFalse(self.user1.is_friend(self.user2))
        self.assertFalse(self.user2.is_friend(self.user1))
        self.assertFalse(self.user2.is_requested_by(self.user1))
        self.assertFalse(self.user1.is_requested_by(self.user2))

    def test_unfriend(self):
        self.user1.send_request_to(self.user2)
        self.user2.accept_request_from(self.user1)
        self.user1.unfriend(self.user2)
        self.assertFalse(self.user1.is_friend(self.user2))
        self.assertFalse(self.user2.is_friend(self.user1))

    def test_follow(self):
        self.user1.follow(self.user2)
        self.assertTrue(self.user1.follows(self.user2))
        self.assertFalse(self.user2.follows(self.user1))

    def test_unfollow(self):
        self.user1.follow(self.user2)
        self.user1.unfollow(self.user2)
        self.assertFalse(self.user1.follows(self.user2))
        self.assertFalse(self.user2.follows(self.user1))
