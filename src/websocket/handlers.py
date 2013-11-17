import tornado.websocket
from websocket.manager import Manager
from auth.models import User


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        manager = Manager.get_manager()
        user = User.objects.find(uid='a672116e8e437feec5499d4ef4b5d2608ee6beb7f31e81f5e8fb45fd')
        manager.register(user.uid, self)

    def on_message(self, message):
        print("Client received a message : %s" % (message))

    def on_close(self):
        manager = Manager.get_manager()
        manager.unregister(self)
