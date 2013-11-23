from data import Redis
from tornado.escape import json_encode, json_decode
import hashlib
from auth import generate_token

TOKEN = 't'
USER = 'u'
REVERSE_USER = 'ru'
FRIENDS = 'f'
FRIEND_REQUESTS = 'fr'
FOLLOWERS = 'fw'


class UserManager:
    def create_user(self, username, fullname, pic=''):
        user = User(hashlib.sha224(generate_token().encode()).hexdigest(),
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

    def to_json(self):
        return json_encode({'username': self.username,
                            'fullname': self.fullname,
                            'pic': self.pic})

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

    def unfriend(self, current_user):
        connection = Redis.get_connection()
        connection.srem("%s:%s" % (FRIENDS, self.uid), current_user.uid)
        connection.srem("%s:%s" % (FRIENDS, current_user.uid), self.uid)

    def follow(self, user):
        connection = Redis.get_connection()
        connection.sadd("%s:%s" % (FOLLOWERS, user.uid), self.uid)

    def unfollow(self, user):
        connection = Redis.get_connection()
        connection.srem("%s:%s" % (FOLLOWERS, user.uid), self.uid)

    def is_followed_by(self, current_user):
        connection = Redis.get_connection()
        return connection.sismember('%s:%s' % (FOLLOWERS, self.uid), current_user.uid)

    def get_followers(self):
        connection = Redis.get_connection()
        return [self.uid] + [follower.decode() for follower in connection.smembers("%s:%s" % (FOLLOWERS, self.uid))]

    objects = UserManager()
