from web import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if user and not user.username:
            self.redirect('/signup')

        self.render("index.html", user=user)
