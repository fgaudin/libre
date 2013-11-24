from data import Redis, TornadoRedis
from tornado.escape import json_encode
from conf import settings
from websocket.manager import Manager

NOTIFICATION = 'n'

ACTIONS = {'follow': 'is following you',
           'request': 'has sent you a friend request',
           'accepted': 'has accepted your friend request',
           'liked': 'has liked your post',
           'commented': 'has commented your post'}


class NotificationManager:
    def create(self, from_username, from_fullname, action, to_uid):
        notif = Notification(from_username, from_fullname, action, to_uid)
        notif.save()
        return notif

    def on_published(self, socket, data):
        manager = Manager.get_manager()
        uid = manager.get_user(socket)
        if uid == data['to_uid']:
            socket.write_message(json_encode({'type': 'notification',
                                              'data': [data]}))


class Notification:
    objects = NotificationManager()

    def __init__(self, from_username, from_fullname, action, to_uid=None, *args, **kwargs):
        if action not in ACTIONS.keys():
            raise Exception('Action not defined')

        self.from_username = from_username
        self.from_fullname = from_fullname
        self.action = action
        self.to_uid = to_uid

    def _to_db(self):
        return {'from_username': self.from_username,
                'from_fullname': self.from_fullname,
                'action': self.action}

    def to_dict(self):
        data = self._to_db()
        data['to_uid'] = self.to_uid
        data['action_str'] = ACTIONS[self.action]
        return data

    def save(self):
        connection = Redis.get_connection()
        connection.lpush('{0}:{1}'.format(NOTIFICATION, self.to_uid),
                         json_encode(self._to_db()))
        connection.ltrim('{0}:{1}'.format(NOTIFICATION, self.to_uid),
                         0,
                         settings.NOTIFICATION_SIZE - 1)

        self.publish()

    def publish(self):
        c = TornadoRedis.get_connection()
        c.publish('main', json_encode({'type': 'notification',
                                       'data': self.to_dict()}))
