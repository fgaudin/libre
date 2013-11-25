from tornado.escape import json_encode
from tornado.web import authenticated
from web import BaseHandler
from notification.models import Notification


class NotificationHandler(BaseHandler):
    @authenticated
    def get(self):
        current_user = self.get_current_user()
        notifications = Notification.objects.get(current_user)

        result = []
        for index, n in enumerate(notifications):
            data = n.to_dict()
            data['id'] = index
            result.append(data)

        response = {'notification': result}
        self.write(json_encode(response))
