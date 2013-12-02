import functools
from tornado.escape import json_encode


def username_set(method):
    """Decorate methods with this to require that the user have set their
    username.

    If the user has not set their username, they will be redirected to
    /signup.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user.username:
            self.set_status(403)
            self.write('You must set your username first')
            return
        return method(self, *args, **kwargs)
    return wrapper
