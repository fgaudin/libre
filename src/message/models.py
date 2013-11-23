from tornado.escape import json_encode, json_decode
from data import Redis, TornadoRedis
from websocket.manager import Manager
import datetime
from user.models import User

MESSAGE_DURATION = 3600
MESSAGES_TO_FRIENDS = 'fm'
MESSAGES_TO_PUBLIC = 'pm'
FRIEND_FEED = 'ff'
PUBLIC_FEED = 'pf'


class MessageManager:
    def get(self, id):
        connection = Redis.get_connection()
        msg = connection.get('m:%s' % id)
        if msg:
            return Message(id=id, ** json_decode(msg))
        return None

    def mget(self, *args, for_me=False):
        if not len(args):
            return []
        connection = Redis.get_connection()
        messages = connection.mget(['m:%s' % id.decode() for id in args])
        return [Message(for_me=for_me, **json_decode(msg)) for msg in messages if msg]

    def get_messages_to_friends(self, user, limit=5):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (MESSAGES_TO_FRIENDS, user.uid), 0, limit))
        return self.mget(*msgs)

    def get_messages_to_public(self, user, limit=5):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (MESSAGES_TO_PUBLIC, user.uid), 0, limit))
        return self.mget(*msgs)

    def get_friends_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (FRIEND_FEED, user.uid), 0, -1))
        return self.mget(*msgs, for_me=True)

    def get_public_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (PUBLIC_FEED, user.uid), 0, -1))
        return self.mget(*msgs, for_me=True)

    def on_published(self, socket, data):
        message = Message(**data)
        manager = Manager.get_manager()
        current_user_uid = manager.get_user(socket)
        if current_user_uid == message.author_uid:
            message.for_me = True
        else:
            current_user = User(current_user_uid, '', '')
            author = User(message.author_uid, message.author_username, message.author_fullname)
            if message.scope == 'public' and author.is_followed_by(current_user):
                message.for_me = True
            elif message.scope == 'friends' and author.is_friend(current_user):
                message.for_me = True

        if message.for_me:
            socket.write_message(json_encode({'type': 'message',
                                              'data': message.to_dict()}))


class Message:
    def __init__(self, scope, body, author_uid, author_username,
                 author_fullname, author_pic, date=None, likes=0,
                 for_me=False, id=None, *args, **kwargs):
        self.id = id
        self.scope = scope
        self.body = body
        self.author_uid = author_uid
        self.author_username = author_username
        self.author_fullname = author_fullname
        self.author_pic = author_pic
        self.date = date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.likes = likes
        self.for_me = for_me

    def to_dict(self):
        return {'id': self.id,
                'scope': self.scope,
                'body': self.body,
                'author_uid': self.author_uid,
                'author_username': self.author_username,
                'author_fullname': self.author_fullname,
                'author_pic': self.author_pic,
                'date': self.date,
                'likes': self.likes,
                'forMe': self.for_me}

    def _to_db(self):
        return {'id': self.id,
                'scope': self.scope,
                'body': self.body,
                'author_uid': self.author_uid,
                'author_username': self.author_username,
                'author_fullname': self.author_fullname,
                'author_pic': self.author_pic,
                'date': self.date,
                'likes': self.likes}

    def _nextId(self):
        connection = Redis.get_connection()
        return connection.incr('msg_id')

    def save(self):
        if not self.id:
            self.id = self._nextId()
            connection = Redis.get_connection()
            connection.setex('m:%s' % self.id, MESSAGE_DURATION, json_encode(self._to_db()))

    def push_to_self(self, current_user):
        connection = Redis.get_connection()
        scope = MESSAGES_TO_PUBLIC if self.scope == 'public' else MESSAGES_TO_FRIENDS
        connection.rpush("%s:%s" % (scope, current_user.uid), self.id)

    def push_to_friends(self, user):
        connection = Redis.get_connection()
        manager = Manager.get_manager()

        friends = user.get_friends()
        for friend in friends:
            connection.rpush('%s:%s' % (FRIEND_FEED, friend), self.id)

    def push_to_public(self, user):
        connection = Redis.get_connection()
        manager = Manager.get_manager()

        friends = user.get_friends()
        for friend in friends:
            connection.rpush('%s:%s' % (PUBLIC_FEED, friend), self.id)

        followers = user.get_followers()
        for follower in followers:
            connection.rpush('%s:%s' % (PUBLIC_FEED, follower), self.id)

    def push(self, current_user):
        self.push_to_self(current_user)
        if self.scope == 'friends':
            self.push_to_friends(current_user)
        elif self.scope == 'public':
            self.push_to_public(current_user)

        self.publish()

    def publish(self):
        c = TornadoRedis.get_connection()
        c.publish('main', json_encode({'type': 'message',
                                       'data': self.to_dict()}))

    objects = MessageManager()
