import redis
import tornadoredis
from conf import settings


class Redis():
    connection = None

    @classmethod
    def get_connection(cls):
        if not cls.connection:
            pool = redis.ConnectionPool(**settings.REDIS)
            cls.connection = redis.StrictRedis(connection_pool=pool)

        return cls.connection


class TornadoRedis:
    connection = None

    @classmethod
    def get_connection(cls):
        if not cls.connection:
            cls.connection = tornadoredis.Client(
                settings.REDIS['host'],
                settings.REDIS['port'],
                password=settings.REDIS['password'],
                selected_db=settings.REDIS['db'])
            cls.connection.connect()

        return cls.connection

IDS = 'id'


def next_id(key):
    connection = Redis.get_connection()
    return connection.hincrby(IDS, key)
