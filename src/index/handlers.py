import tornado.web


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", user=self.get_current_user())
