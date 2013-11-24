from data import Redis, TornadoRedis
from tornado.escape import json_encode, json_decode
import hashlib
from message.models import MESSAGES_TO_FRIENDS, MESSAGES_TO_PUBLIC, FRIEND_FEED, \
    PUBLIC_FEED, Message
from websocket.manager import Manager
from conf import settings

TOKEN = 't'
USER = 'u'
REVERSE_USER = 'ru'
FRIENDS = 'f'
FRIEND_REQUESTS = 'fr'
FOLLOWERS = 'fw'
LIKES = 'l'
USER_COUNTERS = 'uc'


class UserManager:
    def _nextId(self):
        connection = Redis.get_connection()
        return connection.incr('user_id')

    def create_user(self, username, fullname, pic=''):
        user = User(self._nextId(),
                    username,
                    fullname,
                    pic=pic)
        user.save()
        return user

    def find(self, token=None, uid=None, raw_uid=None, username=None):
        connection = Redis.get_connection()
        if token:
            uid = connection.get('%s:%s' % (TOKEN, token))
            if uid:
                uid = uid.decode()
        if raw_uid:
            uid = hashlib.sha224(raw_uid.encode('utf-8')).hexdigest()

        user = None
        if uid:
            user = connection.get('%s:%s' % (USER, uid))
        elif username:
            user = connection.get('%s:%s' % (REVERSE_USER, username))

        if user:
            return User(**json_decode(user))

        return None


class UserAlreadyExists(Exception):
    pass


class User:
    def __init__(self, uid, username, fullname, pic=''):
        self.uid = uid
        self.username = username
        self.fullname = fullname
        self.pic = pic

        self._counters = None

    def to_dict(self):
        return {'id': self.username,
                'uid': self.uid,
                'username': self.username,
                'fullname': self.fullname,
                'pic': self.pic
                }

    def _to_db(self):
        return {'uid': self.uid,
                'username': self.username,
                'fullname': self.fullname,
                'pic': self.pic}

    def save(self):
        connection = Redis.get_connection()
        if not connection.setnx('%s:%s' % (USER, self.uid),
                                json_encode(self._to_db())):
            raise UserAlreadyExists()

        connection.set('%s:%s' % (REVERSE_USER, self.username),
                                  json_encode(self._to_db()))
        connection.hmset('{0}:{1}'.format(USER_COUNTERS, self.uid),
                                          {'friends': 0,
                                           'followers': 0,
                                           'following': 0,
                                           'messages': 0})

    def update(self, username, fullname):
        connection = Redis.get_connection()
        if self.username != username:
            if not connection.setnx('%s:%s' % (REVERSE_USER, username),
                                    ''):
                raise UserAlreadyExists()
            else:
                connection.delete('%s:%s' % (REVERSE_USER, self.username))

        self.username = username
        self.fullname = fullname

        connection.set('%s:%s' % (USER, self.uid),
                       json_encode(self._to_db()))
        connection.set('%s:%s' % (REVERSE_USER, self.username),
                                  json_encode(self._to_db()))

    def authenticate(self, token):
        connection = Redis.get_connection()
        connection.setex('%s:%s' % (TOKEN, token), 3600, self.uid)

    def is_friend(self, current_user):
        if self.uid == current_user.uid:
            return True
        connection = Redis.get_connection()
        return connection.sismember('%s:%s' % (FRIENDS, self.uid), current_user.uid)

    def is_requested_by(self, current_user):
        connection = Redis.get_connection()
        return connection.sismember('%s:%s' % (FRIEND_REQUESTS, self.uid), current_user.uid)

    def get_friends(self):
        connection = Redis.get_connection()
        return [self.uid] + [friend.decode() for friend in connection.smembers("%s:%s" % (FRIENDS, self.uid))]

    def add_request_from(self, current_user):
        connection = Redis.get_connection()
        connection.sadd("%s:%s" % (FRIEND_REQUESTS, self.uid), current_user.uid)
        current_user.follow(self)

    def cancel_request_from(self, current_user):
        connection = Redis.get_connection()
        connection.srem("%s:%s" % (FRIEND_REQUESTS, self.uid), current_user.uid)

    def accept_request_from(self, user):
        connection = Redis.get_connection()
        connection.sadd("%s:%s" % (FRIENDS, self.uid), user.uid)
        connection.sadd("%s:%s" % (FRIENDS, user.uid), self.uid)
        self.cancel_request_from(user)
        self.incr_counter('friends')
        user.incr_counter('friends')

    def unfriend(self, current_user):
        connection = Redis.get_connection()
        connection.srem("%s:%s" % (FRIENDS, self.uid), current_user.uid)
        connection.srem("%s:%s" % (FRIENDS, current_user.uid), self.uid)
        self.decr_counter('friends')
        current_user.decr_counter('friends')

    def follow(self, user):
        connection = Redis.get_connection()
        connection.sadd("%s:%s" % (FOLLOWERS, user.uid), self.uid)
        last_messages = Message.objects.get_messages_to_public(self, user)
        for msg in last_messages:
            connection.lpush('%s:%s' % (PUBLIC_FEED, self.uid), msg.id)
        self.send_messages(last_messages)
        self.incr_counter('following')
        user.incr_counter('followers')

    def unfollow(self, user):
        connection = Redis.get_connection()
        connection.srem("%s:%s" % (FOLLOWERS, user.uid), self.uid)
        self.decr_counter('following')
        user.decr_counter('followers')

    def is_followed_by(self, current_user):
        if self.uid == current_user.uid:
            return True
        connection = Redis.get_connection()
        return connection.sismember('%s:%s' % (FOLLOWERS, self.uid),
                                    current_user.uid)

    def get_followers(self):
        connection = Redis.get_connection()
        return [follower.decode() for follower in connection.smembers("%s:%s" % (FOLLOWERS, self.uid))]

    def get_counters(self):
        if not self._counters:
            connection = Redis.get_connection()
            result = connection.hmget('{0}:{1}'.format(USER_COUNTERS, self.uid),
                                      ['friends', 'followers',
                                       'following', 'messages'])
            self._counters = {'friends': int(result[0]),
                              'followers': int(result[1]),
                              'following': int(result[2]),
                              'messages': int(result[3])}

    def _get_counter(self, counter):
        self.get_counters()
        return self._counters[counter]

    def get_friend_count(self):
        return self._get_counter('friends')

    def get_follower_count(self):
        return self._get_counter('followers')

    def get_following_count(self):
        return self._get_counter('following')

    def get_message_count(self):
        return self._get_counter('messages')

    def incr_counter(self, counter):
        connection = Redis.get_connection()
        connection.hincrby('{0}:{1}'.format(USER_COUNTERS, self.uid),
                           counter)

    def decr_counter(self, counter):
        connection = Redis.get_connection()
        connection.hincrby('{0}:{1}'.format(USER_COUNTERS, self.uid),
                           counter,
                           - 1)

    def get_liked(self):
        connection = Redis.get_connection()
        return connection.smembers('{0}:{1}'.format(LIKES, self.uid))

    def likes(self, msg_id):
        connection = Redis.get_connection()
        return connection.sismember('{0}:{1}'.format(LIKES, self.uid),
                                    msg_id)

    def like(self, msg_id):
        connection = Redis.get_connection()
        connection.sadd('{0}:{1}'.format(LIKES, self.uid), msg_id)
        message = Message(id=msg_id)
        message.incr_like()

    def unlike(self, msg_id):
        connection = Redis.get_connection()
        connection.srem('{0}:{1}'.format(LIKES, self.uid), msg_id)
        message = Message(id=msg_id)
        message.decr_like()

    def send_messages(self, messages, uid=None):
        manager = Manager.get_manager()
        sockets = manager.get_sockets(uid or self.uid)
        data = []
        for m in messages:
            m.for_me = True
            data.append(m.to_dict())

        for socket in sockets:
            socket.write_message({'type': 'message',
                                  'data': data})

    def push_message(self, msg):
        self.push_to_self(msg)
        if msg.scope == 'friends':
            self.push_to_friends(msg)
        elif msg.scope == 'public':
            self.push_to_public(msg)

        self.publish(msg)

    def push_to_self(self, msg):
        connection = Redis.get_connection()
        scope = MESSAGES_TO_PUBLIC if msg.scope == 'public' else MESSAGES_TO_FRIENDS
        connection.lpush("{0}:{1}".format(scope, self.uid), msg.id)
        connection.ltrim("{0}:{1}".format(scope, self.uid), 0, settings.FEED_SIZE - 1)

    def push_to_friends(self, msg):
        connection = Redis.get_connection()

        friends = self.get_friends()
        for friend in friends:
            connection.lpush("{0}:{1}".format(FRIEND_FEED, friend), msg.id)
            connection.ltrim("{0}:{1}".format(FRIEND_FEED, friend), 0, settings.FEED_SIZE - 1)

    def push_to_public(self, msg):
        connection = Redis.get_connection()

        friends = self.get_friends()
        for friend in friends:
            connection.lpush("{0}:{1}".format(PUBLIC_FEED, friend), msg.id)
            connection.ltrim("{0}:{1}".format(PUBLIC_FEED, friend), 0, settings.FEED_SIZE - 1)

        followers = self.get_followers()
        for follower in followers:
            connection.lpush("{0}:{1}".format(PUBLIC_FEED, follower), msg.id)
            connection.ltrim("{0}:{1}".format(PUBLIC_FEED, follower), 0, settings.FEED_SIZE - 1)

    def publish(self, msg):
        c = TornadoRedis.get_connection()
        c.publish('main', json_encode({'type': 'message',
                                       'data': msg.to_dict()}))

    objects = UserManager()
