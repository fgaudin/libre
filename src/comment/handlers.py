from web import BaseHandler
from comment.models import Comment
from tornado.escape import json_encode


class CommentHandler(BaseHandler):
    def get(self):
        message_id = self.get_argument('message_id')
        comments = Comment.objects.find(message_id)
        self.write(json_encode({'comment': [c.to_dict() for c in comments]}))

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

        self.write(json_encode({'commented': True}))
