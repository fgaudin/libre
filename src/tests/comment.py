from tornado.testing import AsyncTestCase, gen_test
from data import Redis
from user.models import User
from message.models import Message
from comment.models import Comment


class CommentTest(AsyncTestCase):
    def setUp(self):
        super(CommentTest, self).setUp()
        connection = Redis.get_connection()
        connection.flushall()

        self.user1 = User.objects.create('foo',
                                              'John Doe',
                                              'http://test.com/img.jpg')

        self.user2 = User.objects.create('foo2',
                                              'John Doe2',
                                              'http://test.com/img2.jpg')

    def tearDown(self):
        super(CommentTest, self).tearDown()
        connection = Redis.get_connection()
        connection.flushall()

    @gen_test
    def test_comment(self):
        message = yield Message.objects.create(
            self.user1,
            'Hello world',
            'friends')

        comment = Comment.objects.create(self.user2, 'First comment', message)

        self.assertEqual(message.comment_count(), 1)
        comments = Comment.objects.find(message.id)
        self.assertEqual(comment.to_dict(), comments[0].to_dict())
