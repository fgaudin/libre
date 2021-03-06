import tornado.testing
import unittest

TEST_MODULES = [
    'tests.auth',
    'tests.comment',
    'tests.data',
    'tests.message',
    'tests.notification',
    'tests.user',
    'tests.websocket',
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


if __name__ == '__main__':
    tornado.testing.main()
