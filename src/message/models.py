from tornado.escape import json_encode, json_decode
from data import Redis, next_id
from websocket.manager import Manager
import datetime
from conf import settings
from comment.models import COMMENT

MESSAGE = 'm'
MESSAGE_COUNTERS = 'mc'
MESSAGES_TO_FRIENDS = 'fm'
MESSAGES_TO_PUBLIC = 'pm'
FRIEND_FEED = 'ff'
PUBLIC_FEED = 'pf'


class MessageManager:
    def get(self, id):
        connection = Redis.get_connection()
        msg = connection.get('{0}:{1}'.format(MESSAGE, id))
        if msg:
            return Message(**json_decode(msg))
        return None

    def mget(self, *args):
        if not len(args):
            return []
        connection = Redis.get_connection()
        messages = connection.mget(['{0}:{1}'.format(MESSAGE, id.decode()) for id in args])
        return [json_decode(msg) for msg in messages if msg]
        # return [Message(for_me=for_me, **json_decode(msg)) for msg in messages if msg]

    def get_messages_to_friends(self, user, limit=5):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (MESSAGES_TO_FRIENDS, user.uid), 0, limit))
        liked = user.get_liked()
        return [Message(for_me=True, liked=(str(msg['id']).encode() in liked), **msg) for msg in self.mget(*msgs)]

    def get_messages_to_public(self, current_user, user, limit=5):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (MESSAGES_TO_PUBLIC, user.uid), 0, limit))
        liked = user.get_liked()
        for_me = False
        if current_user.is_friend(user) or user.is_followed_by(current_user):
            for_me = True
        return [Message(for_me=for_me, liked=(str(msg['id']).encode() in liked), **msg) for msg in self.mget(*msgs)]

    def get_friends_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (FRIEND_FEED, user.uid), 0, -1))
        liked = user.get_liked()
        return [Message(for_me=True, liked=(str(msg['id']).encode() in liked), **msg) for msg in self.mget(*msgs)]

    def get_public_feed(self, user):
        connection = Redis.get_connection()
        msgs = []
        msgs.extend(connection.lrange('%s:%s' % (PUBLIC_FEED, user.uid), 0, -1))
        liked = user.get_liked()
        return [Message(for_me=True, liked=(str(msg['id']).encode() in liked), **msg) for msg in self.mget(*msgs)]

    def on_published(self, socket, data):
        from user.models import User
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
                                              'data': [message.to_dict()]}))


class Message:
    def __init__(self, id=None, scope='', body='', author_uid='',
                 author_username='', author_fullname='', author_pic='',
                 date=None, for_me=False, url='', title='', pic='', width='',
                 height='', liked=False, via_username=None,
                 via_fullname=None, *args, **kwargs):

        self.id = id
        self.scope = scope
        self.body = body
        self.author_uid = author_uid
        self.author_username = author_username
        self.author_fullname = author_fullname
        self.author_pic = author_pic
        self.date = date or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.for_me = for_me
        self.liked = liked
        self.via_username = via_username
        self.via_fullname = via_fullname

        self.url = url
        self.title = title
        self.pic = pic
        self.width = width
        self.height = height

        self._counters = None

    def add_link(self, url, title, pic='', width='', height=''):
        self.url = url
        self.title = title
        self.pic = pic
        self.width = width
        self.height = height

    def get_counters(self):
        if not self._counters:
            connection = Redis.get_connection()
            result = connection.hmget('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                                      ['likes', 'comments'])
            self._counters = {'likes': int(result[0]),
                              'comments': int(result[1])}

    def like_count(self):
        self.get_counters()
        return self._counters['likes']

    def incr_like(self):
        connection = Redis.get_connection()
        connection.hincrby('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                           'likes')
        self._counters = None
        self.reset_ttl()

    def decr_like(self):
        connection = Redis.get_connection()
        connection.hincrby('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                           'likes', -1)
        self._counters = None

    def comment_count(self):
        self.get_counters()
        return self._counters['comments']

    def incr_comment(self):
        connection = Redis.get_connection()
        connection.hincrby('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                           'comments')
        self._counters = None
        self.reset_ttl()

    def to_dict(self):
        return {'id': self.id,
                'scope': self.scope,
                'body': self.body,
                'author_uid': self.author_uid,
                'author_username': self.author_username,
                'author_fullname': self.author_fullname,
                'author_pic': self.author_pic,
                'date': self.date,
                'forMe': self.for_me,
                'liked': self.liked,
                'url': self.url,
                'title': self.title,
                'pic': self.pic,
                'width': self.width,
                'height': self.height,
                'like_count': self.like_count(),
                'comment_count': self.comment_count(),
                'via_username': self.via_username,
                'via_fullname': self.via_fullname,
                }

    def _to_db(self):
        return {'id': self.id,
                'scope': self.scope,
                'body': self.body,
                'author_uid': self.author_uid,
                'author_username': self.author_username,
                'author_fullname': self.author_fullname,
                'author_pic': self.author_pic,
                'date': self.date,
                'url': self.url,
                'title': self.title,
                'pic': self.pic,
                'width': self.width,
                'height': self.height,
                'via_username': self.via_username,
                'via_fullname': self.via_fullname,
                }

    def save(self):
        if not self.id:
            self.id = next_id('message')
            connection = Redis.get_connection()
            connection.setex('{0}:{1}'.format(MESSAGE, self.id),
                             settings.MESSAGE_DURATION,
                             json_encode(self._to_db()))
            connection.hmset('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                             {'likes': 0, 'comments': 0})
            connection.expire('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                              settings.MESSAGE_DURATION)

    def reset_ttl(self):
        connection = Redis.get_connection()
        connection.expire('{0}:{1}'.format(MESSAGE, self.id),
                          settings.MESSAGE_DURATION)
        connection.expire('{0}:{1}'.format(MESSAGE_COUNTERS, self.id),
                          settings.MESSAGE_DURATION)
        connection.expire('{0}:{1}'.format(COMMENT, self.id),
                          settings.MESSAGE_DURATION)

    objects = MessageManager()
