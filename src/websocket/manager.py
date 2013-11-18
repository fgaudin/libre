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
        if not user_uid in self.users:
            self.users[user_uid] = []
        self.users[user_uid].append(socket)
        self.sockets[socket] = user_uid

    def unregister(self, socket):
        user = self.get_user(socket)
        for key, s in enumerate(self.users[user]):
            if socket == s:
                del self.users[user][key]
        if not len(self.users[user]):
            del self.users[user]
        del self.sockets[socket]

    def get_sockets(self, user_uid):
        return self.users[user_uid]

    def get_user(self, socket):
        return self.sockets[socket]

    def send_message(self, type, content, user_uid):
        message = {'type': type, 'data': content}
        for socket in self.get_sockets(user_uid):
            socket.write_message(json_encode(message))
