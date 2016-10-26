# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import unittest

from flask import Flask

from flask_xuanzang import Xuanzang
from flask_xuanzang import ugettext, ungettext


class XuanzangTestCase(unittest.TestCase):
    def setUp(self):
        subprocess.check_call(['pybabel', 'compile', '-d',
                               os.path.join('tests', 'translations')])


class GettextTestCase(XuanzangTestCase):
    def setUp(self):
        super(GettextTestCase, self).setUp()

        self.app = Flask(__name__)
        self.app.config['XUANZANG_DEFAULT_LOCALE'] = 'zh_Hans'
        self.xuanzang = Xuanzang(self.app)

    def test_methods(self):
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Hello!'), '你好！')
            self.assertEqual(
                self.xuanzang.ungettext('%(num)s Apple', '%(num)s Apples', 3),
                '3 个苹果',
            )
            self.assertEqual(
                self.xuanzang.ungettext('%(num)s Apple', '%(num)s Apples', 1),
                '1 个苹果',
            )

    def test_free_functions(self):
        with self.app.test_request_context():
            self.assertEqual(ugettext('Hello!'), '你好！')
            self.assertEqual(
                ungettext('%(num)s Apple', '%(num)s Apples', 3),
                '3 个苹果',
            )
            self.assertEqual(
                ungettext('%(num)s Apple', '%(num)s Apples', 1),
                '1 个苹果',
            )


class MultipleAppsGettextTestCase(XuanzangTestCase):
    def setUp(self):
        super(MultipleAppsGettextTestCase, self).setUp()

        self.xuanzang = Xuanzang()

        self.app_a = Flask(__name__)
        self.app_a.config['XUANZANG_DEFAULT_LOCALE'] = 'en_US'
        self.xuanzang.init_app(self.app_a)

        self.app_b = Flask(__name__)
        self.app_b.config['XUANZANG_DEFAULT_LOCALE'] = 'zh_Hans'
        self.xuanzang.init_app(self.app_b)

    def test_methods(self):
        with self.app_a.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Hello!'), 'Hello!')
        with self.app_b.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Hello!'), '你好！')

    def test_free_functions(self):
        with self.app_a.test_request_context():
            self.assertEqual(ugettext('Hello!'), 'Hello!')
        with self.app_b.test_request_context():
            self.assertEqual(ugettext('Hello!'), '你好！')
