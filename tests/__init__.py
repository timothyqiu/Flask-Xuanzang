from __future__ import unicode_literals

import os
import subprocess
import unittest

from flask import Flask


class XuanzangTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Make sure mo files are generated
        subprocess.check_call(['pybabel', '-q', 'compile', '-d',
                               os.path.join(os.path.dirname(__file__),
                                            'translations')])

    def create_app(self, default_locale):
        app = Flask(__name__)
        app.config.update({
            'TESTING': True,
            'XUANZANG_DEFAULT_LOCALE': default_locale,
        })
        return app
