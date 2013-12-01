import random
import string
import hashlib
from data import Redis
EMAIL = 'e'


def generate_token():
    token = ''.join(random.choice(string.ascii_letters) for i in range(20))
    return hashlib.sha224(token.encode('utf-8')).hexdigest()


def unsalted_hash(phrase):
    result = '{0}'.format(hashlib.sha224(phrase.encode('utf-8')).hexdigest())
    return result


def salted_hash(phrase, salt=None):
    if not salt:
        salt = ''.join(random.choice(string.ascii_letters) for i in range(5))
    data = '{0}{1}'.format(salt, phrase)
    result = '{0}${1}'.format(salt, hashlib.sha224(data.encode('utf-8')).hexdigest())
    return result


def verify_hash(phrase, hashed):
    salt = hashed.split('$')[0]
    return salted_hash(phrase, salt) == hashed


def store_credentials(uid, email, password):
    connection = Redis.get_connection()
    connection.hmset('{0}:{1}'.format(EMAIL, email),
                     {'pwd': salted_hash(password),
                      'uid': uid})


def email_exists(email):
    connection = Redis.get_connection()
    return connection.exists('%s:%s' % (EMAIL, email))


def get_identity(email, password):
    connection = Redis.get_connection()
    result = connection.hmget('%s:%s' % (EMAIL, email), ['pwd', 'uid'])
    if result[0]:
        hashed_pwd = result[0].decode('utf-8')
        uid = result[1].decode('utf-8')
        if hashed_pwd and uid and verify_hash(password, hashed_pwd):
            return uid

    return None
