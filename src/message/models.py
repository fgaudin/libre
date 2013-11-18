from tornado.escape import json_encode, json_decode
from data import Redis
from websocket.manager import Manager
import datetime

FRIEND_FEED = 'ff'
PUBLIC_FEED = 'pf'


class MessageManager:
    def get(self, id):
        connection = Redis.get_connection()
        msg = connection.get('m:%s' % id)
        if msg:
            return Message(id=id, ** json_decode(msg))
        return None

    def mget(self, *args):
        if not len(args):
            return []
        connection = Redis.get_connection()
        messages = connection.mget(['m:%s' % id.decode() for id in args])
        return [Message(**json_decode(msg)) for msg in messages if msg]

    def get_friends_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (FRIEND_FEED, user.uid), 0, -1))
        return self.mget(*msgs)

    def get_public_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (PUBLIC_FEED, user.uid), 0, -1))
        return self.mget(*msgs)


class Message:
    def __init__(self, scope, body, author, date=None, likes=0, id=None):
        self.id = id
        self.scope = scope
        self.body = body
        self.author = author
        self.date = date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.likes = likes

    def to_dict(self):
        return {'id': self.id,
                'scope': self.scope,
                'body': self.body,
                'author': self.author,
                'date': self.date,
                'likes': self.likes}

    def _nextId(self):
        connection = Redis.get_connection()
        return connection.incr('msg_id')

    def save(self):
        if not self.id:
            self.id = self._nextId()
            connection = Redis.get_connection()
            connection.setex('m:%s' % self.id, 60, json_encode(self.to_dict()))

    def push_to_friends(self, user):
        friends = user.get_friends()
        connection = Redis.get_connection()
        manager = Manager.get_manager()
        for friend in friends:
            connection.rpush('%s:%s' % (FRIEND_FEED, friend), self.id)
            manager.send_message('message', self.to_dict(), friend)

    def push_to_public(self, user):
        friends = user.get_friends()
        for friend in friends:
            connection = Redis.get_connection()
            connection.rpush('%s:%s' % (PUBLIC_FEED, friend), self.id)

    def push(self, user):
        if self.scope == 'friends':
            return self.push_to_friends(user)
        elif self.scope == 'public':
            return self.push_to_public(user)

    objects = MessageManager()
