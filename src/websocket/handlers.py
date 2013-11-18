import tornado.websocket
from websocket.manager import Manager
from auth.models import User


class WebSocketHandler(tornado.websocket.WebSocketHandler):
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
            manager = Manager.get_manager()
            manager.register(user.uid, self)

    def on_message(self, message):
        print("Client received a message : %s" % (message))

    def on_close(self):
        print("Client closed")
        manager = Manager.get_manager()
        manager.unregister(self)
