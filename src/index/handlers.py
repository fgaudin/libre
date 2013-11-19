from web import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html", user=self.get_current_user())
