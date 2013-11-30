import tornado.testing
import unittest

TEST_MODULES = [
    'tests.data',
    'tests.user',
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


if __name__ == '__main__':
    tornado.testing.main()
