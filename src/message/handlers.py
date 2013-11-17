import tornado.web
import datetime
from tornado.escape import json_encode, json_decode
from tornado.web import authenticated
from web import BaseHandler
from message.models import Message


class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        feeds = [
            {'id': 'friends',
             'messages': [1, 2]
            },
            {'id': 'public',
             'messages': [3, 4]
            }
        ]
        messages = [
            {'id':1,
             'body': 'Pouet',
             'author': 'Obama',
             'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
             'liked': True
            },
            {'id':2,
             'body': 'Pouet2',
             'author': 'Bush',
             'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
             'liked': False
            },
            {'id':3,
             'body': 'Truc',
             'author': 'Clinton',
             'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
             'liked': True},
            {'id':4,
             'body': 'Bar',
             'author': 'Washington',
             'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
             'liked': False},
        ]

        response = {'feed': feeds,
                    'message': messages}
        self.write(json_encode(response))


class MessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.objects.find(message_id)
        response = {'message': {
            'id': message.id,
            'body': message.body,
            'author': message.author,
            'date': message.date,
            'liked': message.liked
        }}
        self.write(json_encode(response))

    @authenticated
    def post(self):
        data = json_decode(self.request.body)
        message = data['message']
        message['author'] = self.get_current_user().fullname
        del message['feed']
        msg_obj = Message(**message)
        response = {'message': {
            'id': msg_obj.id,
            'body': msg_obj.body,
            'author': msg_obj.author,
            'date': msg_obj.date,
            'liked': msg_obj.liked
        }}
        self.write(json_encode(response))
