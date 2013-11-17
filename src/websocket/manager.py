from tornado.escape import json_encode
class Manager:
    manager = None

    @classmethod
    def get_manager(cls):
        if not cls.manager:
            cls.manager = cls()
        return cls.manager

    def __init__(self):
        self.users = {}
        self.sockets = {}

    def register(self, user_uid, socket):
        self.users[user_uid] = socket
        self.sockets[socket] = user_uid

    def unregister(self, socket):
        del self.users[self.sockets[socket]]
        del self.sockets[socket]

    def get_socket(self, user_uid):
        return self.users[user_uid]

    def get_user(self, socket):
        return self.sockets[socket]

    def send_message(self, type, content, user_uid):
        message = {'type': type, 'data': content}
        self.get_socket(user_uid).write_message(json_encode(message))
