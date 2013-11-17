from tornado.escape import json_encode, json_decode
from tornado.web import authenticated
from web import BaseHandler
from message.models import Message


class MessageHandler(BaseHandler):
    @authenticated
    def get(self, message_id=None):
        user = self.get_current_user()
        if message_id:
            message = Message.objects.get(message_id)
            response = {'message': message.to_dict()}
            self.write(json_encode(response))
        else:
            scope = self.get_argument('scope', None)
            messages = []
            if scope == 'friends':
                messages = Message.objects.get_friends_feed(user)
            elif scope == 'public':
                messages = Message.objects.get_public_feed(user)
            response = {'message': [m.to_dict() for m in messages]}

        self.write(json_encode(response))

    @authenticated
    def post(self):
        user = self.get_current_user()
        data = json_decode(self.request.body)
        message = data['message']
        message['author'] = user.fullname
        del message['liked']
        msg_obj = Message(**message)
        msg_obj.save()
        msg_obj.push(user)

        response = {'message': msg_obj.to_dict()}
        self.write(json_encode(response))
