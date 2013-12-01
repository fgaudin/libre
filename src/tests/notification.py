from tornado.testing import AsyncTestCase, gen_test
from data import Redis
from user.models import User
from notification.models import Notification
from message.models import Message
from comment.models import Comment
import unittest


class NotificationTest(AsyncTestCase):
    def setUp(self):
        super(NotificationTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

        self.user1 = User.objects.create_user('foo',
                                              'John Doe',
                                              'http://test.com/img.jpg')

        self.user2 = User.objects.create_user('foo2',
                                              'John Doe2',
                                              'http://test.com/img2.jpg')

    def tearDown(self):
        super(NotificationTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    def test_follow(self):
        self.user1.follow(self.user2)
        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 0)
        self.assertEqual(len(notifications2), 1)

        notification = notifications2[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user1.fullname)
        self.assertEqual(notification.action, 'follow')
        self.assertEqual(notification.link_param, self.user1.username)
        self.assertEqual(notification.new, True)

    def test_request(self):
        self.user1.send_request_to(self.user2)
        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 0)
        self.assertEqual(len(notifications2), 2)

        # second notification is for following
        notification = notifications2[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user1.fullname)
        self.assertEqual(notification.action, 'request')
        self.assertEqual(notification.link_param, self.user1.username)
        self.assertEqual(notification.new, True)

    def test_accept(self):
        self.user1.send_request_to(self.user2)
        self.user2.accept_request_from(self.user1)
        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 1)
        self.assertEqual(len(notifications2), 2)

        notification = notifications1[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user2.fullname)
        self.assertEqual(notification.action, 'accepted')
        self.assertEqual(notification.link_param, self.user2.username)
        self.assertEqual(notification.new, True)

    @gen_test
    def test_like(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends')

        self.user2.like(message.id)
        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 1)
        self.assertEqual(len(notifications2), 0)

        notification = notifications1[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user2.fullname)
        self.assertEqual(notification.action, 'liked')
        self.assertEqual(notification.link_param, message.id)
        self.assertEqual(notification.new, True)

    @gen_test
    def test_comment(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends')

        Comment.objects.create(self.user2, 'First comment', message)
        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 1)
        self.assertEqual(len(notifications2), 0)

        notification = notifications1[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user2.fullname)
        self.assertEqual(notification.action, 'commented')
        self.assertEqual(notification.link_param, message.id)
        self.assertEqual(notification.new, True)

    @gen_test
    def test_repost(self):
        message = yield Message.objects.create_message(
            self.user1,
            'Hello world',
            'friends',
            self.user2.username)

        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 0)
        self.assertEqual(len(notifications2), 1)

        notification = notifications2[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user1.fullname)
        self.assertEqual(notification.action, 'reposted')
        self.assertEqual(notification.link_param, message.id)
        self.assertEqual(notification.new, True)

    @gen_test
    def test_mention(self):
        message = yield Message.objects.create_message(
            self.user1,
            'hello @foo2',
            'friends')

        notifications1 = Notification.objects.get(self.user1)
        notifications2 = Notification.objects.get(self.user2)

        self.assertEqual(len(notifications1), 0)
        self.assertEqual(len(notifications2), 1)

        notification = notifications2[0]
        self.assertGreater(notification.id, 0)
        self.assertEqual(notification.from_fullname, self.user1.fullname)
        self.assertEqual(notification.action, 'mentioned')
        self.assertEqual(notification.link_param, message.id)
        self.assertEqual(notification.new, True)
