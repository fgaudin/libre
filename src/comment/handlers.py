from web import BaseHandler
from comment.models import Comment
from tornado.escape import json_encode
from websocket.manager import Manager
from tornado.web import authenticated


class CommentHandler(BaseHandler):
    @authenticated
    def get(self):
        user = self.get_current_user()
        message_id = self.get_argument('message_id')
        manager = Manager.get_manager()
        sockets = manager.get_sockets(user.uid)
        for socket in sockets:
            socket.listen_to_message(message_id)

        comments = Comment.objects.find(message_id)
        self.write(json_encode({'comment': [c.to_dict() for c in comments]}))

    @authenticated
    def post(self):
        message_id = self.get_argument('message_id')
        comment_content = self.get_argument('comment')
        user = self.get_current_user()

        comment = Comment(user.uid,
                          user.username,
                          user.fullname,
                          user.pic,
                          comment_content,
                          message_id)
        comment.save()
        comment.publish()

        self.write(json_encode({'commented': True}))
