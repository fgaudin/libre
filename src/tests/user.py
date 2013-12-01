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

    def test_search(self):
        user1 = User.objects.create_user('foo1',
                                         'John Doe',
                                         'http://test.com/img.jpg')
        user2 = User.objects.create_user('foo2',
                                         'Jane Doe',
                                         'http://test.com/img.jpg')
        user3 = User.objects.create_user('zoo',
                                         'John Doe',
                                         'http://test.com/img.jpg')

        results = User.objects.search('foo')
        self.assertEqual(len(results), 2)
        self.assertIn(user1.to_dict(), results)
        self.assertIn(user2.to_dict(), results)

        results = User.objects.search('foo1')
        self.assertEqual(len(results), 1)
        self.assertIn(user1.to_dict(), results)

        results = User.objects.search('oo')
        self.assertEqual(len(results), 3)
        self.assertIn(user1.to_dict(), results)
        self.assertIn(user2.to_dict(), results)
        self.assertIn(user3.to_dict(), results)


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

        self.user3 = User.objects.create_user('foo3',
                                              'John Doe3',
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

    def test_get_friend_count(self):
        self.user1.send_request_to(self.user2)
        self.user2.accept_request_from(self.user1)
        self.user1.send_request_to(self.user3)
        self.user3.accept_request_from(self.user1)
        self.assertEqual(self.user1.get_friend_count(), 2)
        self.assertEqual(self.user2.get_friend_count(), 1)
        self.assertEqual(self.user3.get_friend_count(), 1)

    def test_follow(self):
        self.user1.follow(self.user2)
        self.assertTrue(self.user1.follows(self.user2))
        self.assertFalse(self.user2.follows(self.user1))

    def test_unfollow(self):
        self.user1.follow(self.user2)
        self.user1.unfollow(self.user2)
        self.assertFalse(self.user1.follows(self.user2))
        self.assertFalse(self.user2.follows(self.user1))

    def test_get_follower_count(self):
        self.user1.follow(self.user3)
        self.user2.follow(self.user3)
        self.assertEqual(self.user3.get_follower_count(), 2)

    def test_get_following_count(self):
        self.user1.follow(self.user2)
        self.user1.follow(self.user3)
        self.assertEqual(self.user1.get_following_count(), 2)
