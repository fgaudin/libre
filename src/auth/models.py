from data import Redis
from tornado.escape import json_encode, json_decode
import hashlib


class UserManager:
    def create_user(self, uid, username, fullname):
        user = User(hashlib.sha224(uid.encode('utf-8')).hexdigest(),
                    username,
                    fullname)
        user.save()

    def find(self, token=None, uid=None):
        connection = Redis.get_connection()
        if token:
            uid = connection.get('t:%s' % token).decode()
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
        return (self.uid,)

    objects = UserManager()
