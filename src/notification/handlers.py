from tornado.escape import json_encode
from tornado.web import authenticated
from web import BaseHandler
from notification.models import Notification


class NotificationHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = self.get_current_user()
        notifications = Notification.objects.get(current_user)
        response = {'notification': [n.to_dict() for n in notifications]}

        self.write(json_encode(response))
