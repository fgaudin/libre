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

    def register(self, user_id, socket):
        if not user_id in self.users:
            self.users[user_id] = []
        self.users[user_id].append(socket)
        self.sockets[socket] = user_id

    def unregister(self, socket):
        user = self.get_user(socket)
        for key, s in enumerate(self.users[user]):
            if socket == s:
                del self.users[user][key]
        if not len(self.users[user]):
            del self.users[user]
        del self.sockets[socket]

    def get_sockets(self, user_id):
        if user_id in self.users:
            return self.users[user_id]
        return []

    def get_user(self, socket):
        return self.sockets[socket]

    def send_message(self, type, content, user_id):
        message = {'type': type, 'data': content}
        for socket in self.get_sockets(user_id):
            socket.write_message(json_encode(message))
