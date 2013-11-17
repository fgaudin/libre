from tornado.escape import json_encode, json_decode
from data import Redis


class MessageManager:
    def find(self, id):
        connection = Redis.get_connection()
        msg = connection.get('m:%s' % id)
        if msg:
            return Message(id=id, ** json_decode(msg))
        return None


class Message:
    def __init__(self, body, author, date, liked, id=None):
        self.id = id
        self.body = body
        self.author = author
        self.date = date
        self.liked = liked

    def to_json(self):
        return json_encode({'body': self.body,
                            'author': self.author,
                            'date': self.date,
                            'liked': self.liked})

    def _nextId(self):
        connection = Redis.get_connection()
        return connection.incr('msg_id')

    def save(self):
        if not self.id:
            self.id = self._nextId()
            connection = Redis.get_connection()
            connection.setex('m:%s' % self.id, 3600, self.to_json())

    objects = MessageManager()
