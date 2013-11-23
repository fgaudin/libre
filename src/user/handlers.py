from tornado.escape import json_encode
from web import BaseHandler
from user.models import User
from tornado.web import authenticated
from websocket.manager import Manager
from message.models import Message


class ProfileHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render("index.html", user=self.get_current_user())

    @authenticated
    def post(self):
        username = self.get_argument('username')
        fullname = self.get_argument('fullname')

        user = self.get_current_user()
        try:
            user.update(username, fullname)
            self.redirect('/')
        except Exception as e:
            print(e)
            self.render("index.html", user=self.get_current_user())


class UserHandler(BaseHandler):
    def get(self, username):
        user = User.objects.find(username=username)
        current_user = self.get_current_user()
        data = user.to_dict()

        data['friend'] = False
        if current_user:
            data['friend'] = user.is_friend(current_user)

        data['friend_requested'] = False
        if current_user:
            data['friend_requested'] = user.is_requested_by(current_user)

        data['friend_waiting'] = False
        if current_user:
            data['friend_waiting'] = current_user.is_requested_by(user)

        data['followed'] = False
        if current_user:
            data['followed'] = user.is_followed_by(current_user)

        response = {'user': data}

        self.write(json_encode(response))

    @authenticated
    def post(self, username):
        action = self.get_argument('action')
        user = User.objects.find(username=username)
        current_user = self.get_current_user()
        response = {}
        if action == "request_friend":
            user.add_request_from(current_user)
            response['friend_requested'] = True
        elif action == "cancel_friend_request":
            user.cancel_request_from(current_user)
            response['friend_requested'] = False
        elif action == "accept_friend":
            current_user.accept_request_from(user)
            response['friend'] = True
        elif action == 'unfriend':
            user.unfriend(current_user)
            response['friend'] = False
        if action == 'follow':
            current_user.follow(user)
            response['followed'] = True
        elif action == 'unfollow':
            current_user.unfollow(user)
            response['followed'] = False

        self.write(json_encode(response))
