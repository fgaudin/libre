from tornado.escape import json_encode
from tornado.web import authenticated
from web import BaseHandler
from message.models import Message
from user.models import User
from tornado import gen
from auth.decorators import username_set


class MessageHandler(BaseHandler):
    def get(self, message_id=None):
        current_user = self.get_current_user()
        if message_id:
            message = Message.objects.get(message_id)
            response = {'message': message.to_dict()}
        else:
            messages = []
            username = self.get_argument('username', None)
            if username:
                user = User.objects.find(username=username)
                if user.is_friend(current_user):
                    messages.extend(Message.objects.get_messages_to_friends(user))
                messages.extend(Message.objects.get_messages_to_public(current_user, user))
            else:
                if current_user:
                    messages = Message.objects.get_friends_feed(current_user) + Message.objects.get_public_feed(current_user)
            response = {'message': [m.to_dict() for m in messages]}

        self.write(json_encode(response))

    @authenticated
    @username_set
    @gen.coroutine
    def post(self):
        user = self.get_current_user()

        via = self.get_argument('via', None)
        body = self.get_argument('body')
        scope = self.get_argument('scope')

        yield Message.objects.create(user,
                                     body,
                                     scope,
                                     via)

        self.write(json_encode({'posted': True}))


class LikeHandler(BaseHandler):
    @authenticated
    @username_set
    def post(self):
        message_id = self.get_argument('message_id')
        user = self.get_current_user()
        liked = False
        if user.likes(message_id):
            user.unlike(message_id)
        else:
            user.like(message_id)
            liked = True

        self.write(json_encode({'liked': liked}))
