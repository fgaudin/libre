from data import Redis, TornadoRedis, next_id
from tornado.escape import json_encode, json_decode
from notification.models import Notification

COMMENT = 'c'


class CommentManager:
    def create(self, user, content, message):
        comment = Comment(user.uid,
                          user.username,
                          user.fullname,
                          user.pic,
                          content,
                          message.id)
        comment.save()
        comment.publish()
        Notification.objects.create(user.fullname,
                                    'commented',
                                    message.id,
                                    message.author_uid)

        return comment

    def count(self, msg_id):
        connection = Redis.get_connection()
        return connection.llen('{0}:{1}'.format(COMMENT, msg_id))

    def find(self, msg_id):
        connection = Redis.get_connection()
        result = connection.lrange('{0}:{1}'.format(COMMENT, msg_id), 0, -1)
        return [Comment(msg_id=msg_id, **json_decode(c)) for c in result]

    def on_published(self, socket, data):
        comment = Comment(**data)
        socket.write_message(json_encode({'type': 'comment',
                                          'data': [comment.to_dict()]}))


class Comment:
    objects = CommentManager()

    def __init__(self, author_id, author_username, author_fullname, author_pic, content, msg_id, id=''):
        self.author_id = author_id
        self.author_username = author_username
        self.author_fullname = author_fullname
        self.author_pic = author_pic
        self.content = content
        self.msg_id = msg_id
        self.id = id

    def _to_db(self):
        return {'id': self.id,
                'author_id': self.author_id,
                'author_username': self.author_username,
                'author_fullname': self.author_fullname,
                'author_pic': self.author_pic,
                'content': self.content}

    def to_dict(self):
        data = self._to_db()
        data['msg_id'] = self.msg_id
        return data

    def save(self):
        from message.models import Message
        connection = Redis.get_connection()
        if not self.id:
            self.id = next_id('comment')
        connection.rpush('{0}:{1}'.format(COMMENT, self.msg_id),
                         json_encode(self._to_db()))
        message = Message(id=self.msg_id)
        message.incr_comment()

    def publish(self):
        c = TornadoRedis.get_connection()
        c.publish('msg:{0}'.format(self.msg_id),
                  json_encode({'type': 'comment',
                               'data': self.to_dict()}))
