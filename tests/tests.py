import unittest

from flask import Flask

from flask_xuanzang import Xuanzang


class TestIntegration(unittest.TestCase):
    def test_dummy(self):
        app = Flask(__name__)
        xuanzang = Xuanzang(app)
