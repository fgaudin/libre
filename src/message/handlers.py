from tornado.escape import json_encode, json_decode, linkify, _URL_RE
from tornado.web import authenticated
from web import BaseHandler
from message.models import Message
from user.models import User
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from bs4 import BeautifulSoup


class MessageHandler(BaseHandler):
    def get(self, message_id=None):
        current_user = self.get_current_user()
        if message_id:
            message = Message.objects.get(message_id)
            response = {'message': message.to_dict()}
            self.write(json_encode(response))
        else:
            messages = []
            username = self.get_argument('username', None)
            if username:
                user = User.objects.find(username=username)
                if user.is_friend(current_user):
                    messages.extend(Message.objects.get_messages_to_friends(user))
                messages.extend(Message.objects.get_messages_to_public(user))
            else:
                if current_user:
                    messages = Message.objects.get_friends_feed(current_user) + Message.objects.get_public_feed(current_user)
            response = {'message': [m.to_dict() for m in messages]}

        self.write(json_encode(response))

    @authenticated
    @gen.coroutine
    def post(self):
        user = self.get_current_user()
        message = {}
        message['scope'] = self.get_argument('scope')
        message['body'] = linkify(self.get_argument('body'))
        message['author_uid'] = user.uid
        message['author_fullname'] = user.fullname
        message['author_username'] = user.username
        message['author_pic'] = user.pic
        message['likes'] = 0
        msg_obj = Message(**message)

        result = _URL_RE.search(self.get_argument('body'))
        if result:
            try:
                url = result.group()
                http_client = AsyncHTTPClient()
                response = yield http_client.fetch(url)
                soup = BeautifulSoup(response.body, 'lxml')

                try:
                    oembed_link = soup.find('link', {'rel': 'alternate', 'type': 'application/json+oembed'}).attrs['href']
                    http_client = AsyncHTTPClient()
                    oembed = yield http_client.fetch(oembed_link)
                    json = json_decode(oembed.body)
                    msg_obj.add_link(url, json['title'], json['thumbnail_url'],
                                     json['thumbnail_width'], json['thumbnail_height'])
                except:
                    title = soup.title
                    if title:
                        msg_obj.add_link(url, title.string)
            except:
                pass

        msg_obj.save()
        user.push_message(msg_obj)

        self.write(json_encode(msg_obj.to_dict()))
