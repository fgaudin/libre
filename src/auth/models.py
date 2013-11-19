from data import Redis
from tornado.escape import json_encode, json_decode
import hashlib

FRIENDS = 'f'
FOLLOWERS = 'fw'


class UserManager:
    def create_user(self, uid, username, fullname):
        user = User(hashlib.sha224(uid.encode('utf-8')).hexdigest(),
                    username,
                    fullname)
        user.save()

    def find(self, token=None, uid=None, raw_uid=None):
        connection = Redis.get_connection()
        if token:
            uid = connection.get('t:%s' % token)
            if uid:
                uid = uid.decode()
        if raw_uid:
            uid = hashlib.sha224(raw_uid.encode('utf-8')).hexdigest()
        if uid:
            user = connection.get('u:%s' % uid)
            if user:
                return User(uid, **json_decode(user))
        return None


class UserAlreadyExists(Exception):
    pass


class User:
    def __init__(self, uid, username, fullname):
        self.uid = uid
        self.username = username
        self.fullname = fullname

    def to_json(self):
        return json_encode({'username': self.username, 'fullname': self.fullname})

    def save(self):
        connection = Redis.get_connection()
        if not connection.setnx('u:%s' % self.uid, self.to_json()):
            raise UserAlreadyExists()

    def authenticate(self, token):
        connection = Redis.get_connection()
        connection.setex('t:%s' % token, 3600, self.uid)

    def get_friends(self):
        connection = Redis.get_connection()
        return [self.uid] + [friend.decode() for friend in connection.smembers("%s:%s" % (FRIENDS, self.uid))]

    def get_followers(self):
        connection = Redis.get_connection()
        return [self.uid] + [follower.decode() for follower in connection.smembers("%s:%s" % (FOLLOWERS, self.uid))]

    objects = UserManager()
