import redis


REDIS = {
    'host':'127.0.0.1',
    'port':6379,
    'password':None,
    'db': 0,
}


class Redis():
    connection = None

    @classmethod
    def get_connection(cls):
        if not cls.connection:
            pool = redis.ConnectionPool(host=REDIS['host'],
                            port=REDIS['port'],
                            db=REDIS['db'],
                            password=REDIS['password'])
            cls.connection = redis.StrictRedis(connection_pool=pool)

        return cls.connection
