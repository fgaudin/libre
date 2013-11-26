import tornado.websocket
from websocket.manager import Manager
from user.models import User
import tornadoredis
import tornado.gen
from tornado.escape import json_decode
from message.models import Message
from comment.models import Comment
from notification.models import Notification


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.manager = Manager.get_manager()
        self.listen()

    def on_published(self, msg):
        if msg.kind == 'message':
            payload = json_decode(msg.body)
            if payload['type'] == 'message':
                Message.objects.on_published(self, payload['data'])
            elif payload['type'] == 'comment':
                Comment.objects.on_published(self, payload['data'])
            elif payload['type'] == 'notification':
                Notification.objects.on_published(self, payload['data'])

        if msg.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated '
                               'due to a Redis server error.')
            self.close()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'main')
        self.client.listen(self.on_published)

    @tornado.gen.engine
    def listen_to_message(self, msg_id):
        yield tornado.gen.Task(self.client.subscribe, 'msg:{0}'.format(msg_id))

    def get_current_user(self):
        token = self.get_secure_cookie("auth")
        return User.objects.find(token.decode())

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self, *args):
        print("New client")
        user = self.get_current_user()
        if user:
            print(user.uid, user.username)
            self.manager.register(user.uid, self)

    def on_message(self, msg):
        message = json_decode(msg)
        if message['type'] == 'search':
            User.objects.search(self, message['term'])

    def on_close(self):
        print("Client closed")
        self.client.disconnect()
        self.manager.unregister(self)
