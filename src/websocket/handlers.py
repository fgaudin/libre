import tornado.websocket


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        print("opened")

    def on_message(self, message):
        print("Client received a message : %s" % (message))

    def on_close(self):
        print("closed")
