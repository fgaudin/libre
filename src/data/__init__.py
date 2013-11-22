import redis
from conf import settings


class Redis():
    connection = None

    @classmethod
    def get_connection(cls):
        if not cls.connection:
            pool = redis.ConnectionPool(**settings.REDIS)
            cls.connection = redis.StrictRedis(connection_pool=pool)

        return cls.connection
