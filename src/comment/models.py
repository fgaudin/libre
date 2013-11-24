from data import Redis
from tornado.escape import json_encode, json_decode
from message.models import Message

COMMENT = 'c'


class CommentManager:
    def find(self, msg_id):
        connection = Redis.get_connection()
        result = connection.lrange('{0}:{1}'.format(COMMENT, msg_id), 0, -1)
        return [Comment(msg_id=msg_id, **json_decode(c)) for c in result]


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

    def _nextId(self):
        connection = Redis.get_connection()
        return connection.incr('c_id')

    def _to_db(self):
        return {'id': self.id  or self._nextId(),
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
        connection = Redis.get_connection()
        connection.rpush('{0}:{1}'.format(COMMENT, self.msg_id),
                         json_encode(self._to_db()))
        message = Message(id=self.msg_id)
        message.incr_comment()
