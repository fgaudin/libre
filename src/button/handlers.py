from web import BaseHandler


class ButtonHandler(BaseHandler):
    def get(self):
        self.render('index.html')
