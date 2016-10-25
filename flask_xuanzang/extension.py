from __future__ import absolute_import


class Xuanzang(object):
    def __init__(self, app=None):
        self.app = app

        if app:
            self.init_app(app)

    def init_app(self, app):
        pass
