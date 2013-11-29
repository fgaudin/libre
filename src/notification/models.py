from data import Redis, TornadoRedis, next_id
from tornado.escape import json_encode, json_decode
from conf import settings
from websocket.manager import Manager

NEW_NOTIFICATION = 'nn'
NOTIFICATION = 'n'

ACTIONS = {'follow': 'is following you',
           'request': 'has sent you a friend request',
           'accepted': 'has accepted your friend request',
           'liked': 'has liked your post',
           'commented': 'has commented your post',
           'reposted': 'has reposted your post',
           'mentioned': 'has mentioned you in a post'}


class NotificationManager:
    def create(self, from_fullname, action, link_param, to_uid):
        notif = Notification(from_fullname, action, link_param, to_uid)
        notif.save()
        return notif

    def get(self, user):
        connection = Redis.get_connection()
        result_new_notif = connection.lrange('{0}:{1}'.format(NEW_NOTIFICATION, user.uid),
                                             0,
                                             settings.NOTIFICATION_SIZE)
        new_notifications = [Notification(**json_decode(n)) for n in result_new_notif]
        result = connection.lrange('{0}:{1}'.format(NOTIFICATION, user.uid),
                                   0,
                                   settings.NOTIFICATION_SIZE)
        notifications = [Notification(new=False, **json_decode(n)) for n in result]

        return new_notifications + notifications

    def seen(self, user):
        connection = Redis.get_connection()
        result_new_notif = connection.lrange('{0}:{1}'.format(NEW_NOTIFICATION,
                                                              user.uid),
                                             0,
                                             settings.NOTIFICATION_SIZE)
        connection.ltrim('{0}:{1}'.format(NEW_NOTIFICATION, user.uid),
                         1,
                         0)

        if result_new_notif:
            connection.lpush('{0}:{1}'.format(NOTIFICATION, user.uid),
                             *result_new_notif)

    def on_published(self, socket, data):
        manager = Manager.get_manager()
        uid = manager.get_user(socket)
        if uid == data['to_uid']:
            socket.write_message(json_encode({'type': 'notification',
                                              'data': [data]}))


class Notification:
    objects = NotificationManager()

    def __init__(self, from_fullname, action, link_param=None, to_uid=None,
                 new=True, id=None, *args, **kwargs):
        if action not in ACTIONS.keys():
            raise Exception('Action not defined')

        self.id = id
        self.from_fullname = from_fullname
        self.action = action
        self.to_uid = to_uid
        self.link_param = link_param
        self.new = new

    def _to_db(self):
        return {'id': self.id,
                'from_fullname': self.from_fullname,
                'action': self.action,
                'link_param': self.link_param}

    def to_dict(self):
        data = self._to_db()
        data['to_uid'] = self.to_uid
        data['action_str'] = ACTIONS[self.action]
        data['new'] = self.new
        return data

    def save(self):
        if not self.id:
            self.id = next_id('notification')
            connection = Redis.get_connection()
            connection.lpush('{0}:{1}'.format(NEW_NOTIFICATION, self.to_uid),
                             json_encode(self._to_db()))

            self.publish()

    def publish(self):
        c = TornadoRedis.get_connection()
        c.publish('main', json_encode({'type': 'notification',
                                       'data': self.to_dict()}))
