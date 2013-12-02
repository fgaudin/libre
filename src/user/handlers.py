from tornado.escape import json_encode, squeeze
from web import BaseHandler
from user.models import User, InvalidUsernameError, InvalidFullnameError, \
    UsernameTakenError
from tornado.web import authenticated
from auth.decorators import username_set


class SignupHandler(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()

        if user.username:
            self.redirect('/')

        user.username = user.objects.get_valid_username(user.fullname)
        self.render("signup.html",
                    user=user,
                    errors=[])

    @authenticated
    def post(self):
        user = self.get_current_user()

        if user.username:
            self.redirect('/')

        username = squeeze(self.get_argument('username', ''))
        fullname = squeeze(self.get_argument('fullname', ''))

        errors = []

        if not username or not fullname:
            errors.append('Username and full name are mandatory')
        else:
            try:
                user.username = username
                user.fullname = fullname
                user.save()
                self.redirect('/')
                return
            except InvalidUsernameError:
                errors.append('Username must contain only letters, numbers and underscores (a-z, 0-9, _)')
            except InvalidFullnameError:
                errors.append('Full name must contain only letters, numbers, underscores and spaces (a-z, 0-9, _)')
            except UsernameTakenError:
                errors.append('This username is already taken')
            except Exception as e:
                errors.append('Unexpected error')

        self.render("signup.html",
                    user=user,
                    errors=errors)


class ProfileHandler(BaseHandler):
    @authenticated
    @username_set
    def get(self):
        user = self.get_current_user()
        friend_ids = user.get_friends()
        friends = User.objects.mget(*friend_ids)
        follower_ids = user.get_followers()
        followers = User.objects.mget(*follower_ids)
        followee_ids = user.get_followees()
        followees = User.objects.mget(*followee_ids)
        self.render("index.html",
                    user=user,
                    friends=friends,
                    followers=followers,
                    followees=followees)


class UserHandler(BaseHandler):
    @authenticated
    @username_set
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

        data['friends'] = user.get_friend_count()
        data['followers'] = user.get_follower_count()
        data['following'] = user.get_following_count()
        data['messages'] = user.get_message_count()

        response = {'user': data}

        self.write(json_encode(response))

    @authenticated
    @username_set
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
