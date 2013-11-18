import tornado.websocket
from websocket.manager import Manager
from auth.models import User


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self, *args):
        print("New client")
        manager = Manager.get_manager()
        user = User.objects.find(uid='a672116e8e437feec5499d4ef4b5d2608ee6beb7f31e81f5e8fb45fd')
        manager.register(user.uid, self)

    def on_message(self, message):
        print("Client received a message : %s" % (message))

    def on_close(self):
        print("Client closed")
        manager = Manager.get_manager()
        manager.unregister(self)
