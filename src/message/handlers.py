from tornado.escape import json_encode, json_decode, linkify
from tornado.web import authenticated
from web import BaseHandler
from message.models import Message


class MessageHandler(BaseHandler):
    def initialize(self, scope=None):
        self.scope = scope

    def get(self, message_id=None):
        user = self.get_current_user()
        if message_id:
            message = Message.objects.get(message_id)
            response = {'message': message.to_dict()}
            self.write(json_encode(response))
        else:
            messages = []
            if user:
                if self.scope == 'friends':
                    messages = Message.objects.get_friends_feed(user)
                elif self.scope == 'public':
                    messages = Message.objects.get_public_feed(user)
                else:
                    messages = Message.objects.get_friends_feed(user) + Message.objects.get_public_feed(user)
            response = {'message': [m.to_dict() for m in messages]}

        self.write(json_encode(response))

    @authenticated
    def post(self):
        user = self.get_current_user()
        message = {}
        message['scope'] = self.get_argument('scope')
        message['body'] = linkify(self.get_argument('body'))
        message['author_fullname'] = user.fullname
        message['author_username'] = user.username
        message['likes'] = 0
        msg_obj = Message(**message)
        msg_obj.save()
        msg_obj.push(user)

        self.write(json_encode(msg_obj.to_dict()))
