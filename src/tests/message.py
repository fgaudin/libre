from tornado.testing import AsyncTestCase, gen_test
from data import Redis
from message.models import Message
from user.models import User


class MessageTest(AsyncTestCase):
    def setUp(self):
        super(MessageTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

        self.user1 = User.objects.create_user('foo',
                                              'John Doe',
                                              'http://test.com/img.jpg')

        self.user2 = User.objects.create_user('foo2',
                                              'John Doe2',
                                              'http://test.com/img2.jpg')

    def tearDown(self):
        super(MessageTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    @gen_test
    def test_create_message(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends')

        self.assertGreater(message.id, 0)

        saved = Message.objects.get(message.id)
        self.assertEqual(saved.scope, 'friends')
        self.assertEqual(saved.body, message.body)
        self.assertEqual(saved.author_id, self.user1.id)
        self.assertEqual(saved.author_username, self.user1.username)
        self.assertEqual(saved.author_fullname, self.user1.fullname)
        self.assertEqual(saved.author_pic, self.user1.pic)
        self.assertEqual(saved.date, message.date)
        self.assertEqual(saved.liked, 0)

    @gen_test
    def test_repost(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends',
            self.user2.username)

        self.assertGreater(message.id, 0)

        saved = Message.objects.get(message.id)
        self.assertEqual(saved.scope, 'friends')
        self.assertEqual(saved.body, message.body)
        self.assertEqual(saved.author_id, self.user1.id)
        self.assertEqual(saved.author_username, self.user1.username)
        self.assertEqual(saved.author_fullname, self.user1.fullname)
        self.assertEqual(saved.author_pic, self.user1.pic)
        self.assertEqual(saved.date, message.date)
        self.assertEqual(saved.liked, 0)
        self.assertEqual(saved.via_username, self.user2.username)
        self.assertEqual(saved.via_fullname, self.user2.fullname)


class LikeTest(AsyncTestCase):
    def setUp(self):
        super(LikeTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

        self.user1 = User.objects.create_user('foo',
                                              'John Doe',
                                              'http://test.com/img.jpg')

        self.user2 = User.objects.create_user('foo2',
                                              'John Doe2',
                                              'http://test.com/img2.jpg')

    def tearDown(self):
        super(LikeTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    @gen_test
    def test_like(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends')

        self.user2.like(message.id)
        saved = Message.objects.get(message.id)
        self.assertEqual(saved.like_count(), 1)

    @gen_test
    def test_unlike(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends')

        self.user2.like(message.id)
        saved = Message.objects.get(message.id)
        self.assertEqual(saved.like_count(), 1)
        self.user2.unlike(message.id)
        saved = Message.objects.get(message.id)
        self.assertEqual(saved.like_count(), 0)
