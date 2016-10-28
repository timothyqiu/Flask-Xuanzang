# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import sys
import unittest

from flask import Flask

from flask_xuanzang import Xuanzang
from flask_xuanzang import gettext, ngettext
from flask_xuanzang import ugettext, ungettext, pgettext, npgettext


PY2 = (sys.version_info[0] == 2)


class XuanzangTestCase(unittest.TestCase):
    def setUp(self):
        subprocess.check_call(['pybabel', 'compile', '-d',
                               os.path.join('tests', 'translations')])


class SingleAppTestCase(XuanzangTestCase):
    def setUp(self):
        super(SingleAppTestCase, self).setUp()

        self.app = Flask(__name__)
        self.app.config['XUANZANG_DEFAULT_LOCALE'] = 'de'
        self.xuanzang = Xuanzang(self.app)


class GettextTestCase(SingleAppTestCase):
    def setUp(self):
        super(GettextTestCase, self).setUp()

    def test_gettext(self):
        with self.app.test_request_context():
            message = gettext('Large')
            if PY2:
                self.assertEqual(message, 'Groß'.encode('utf-8'))
            else:
                self.assertEqual(message, 'Groß')

    def test_ngettext(self):
        with self.app.test_request_context():
            singular = ngettext('%(num)s apple', '%(num)s apples', 1)
            plural = ngettext('%(num)s apple', '%(num)s apples', 2)

            if PY2:
                self.assertEqual(singular, '1 Apfel'.encode('utf-8'))
                self.assertEqual(plural, '2 Äpfel'.encode('utf-8'))
            else:
                self.assertEqual(singular, '1 Apfel')
                self.assertEqual(plural, '2 Äpfel')

    def test_ugettext(self):
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')

    def test_ungettext(self):
        with self.app.test_request_context():
            singular = ungettext('%(num)s apple', '%(num)s apples', 1)
            plural = ungettext('%(num)s apple', '%(num)s apples', 2)
            self.assertEqual(singular, '1 Apfel')
            self.assertEqual(plural, '2 Äpfel')

    def test_pgettext(self):
        with self.app.test_request_context():
            self.assertEqual(pgettext('month name', 'May'), 'Mai')

    def test_npgettext(self):
        with self.app.test_request_context():
            singular = npgettext('fruits', 'apple', 'apples', 1)
            plural = npgettext('fruits', 'apple', 'apples', 2)
            self.assertEqual(singular, 'Apfel')
            self.assertEqual(plural, 'Äpfel')


class MethodTestCase(SingleAppTestCase):
    def test_gettext(self):
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Groß')


class MultipleAppsTestCase(XuanzangTestCase):
    def setUp(self):
        super(MultipleAppsTestCase, self).setUp()

        self.xuanzang = Xuanzang()

        self.app_a = Flask(__name__)
        self.app_a.config['XUANZANG_DEFAULT_LOCALE'] = 'en'
        self.xuanzang.init_app(self.app_a)

        self.app_b = Flask(__name__)
        self.app_b.config['XUANZANG_DEFAULT_LOCALE'] = 'de'
        self.xuanzang.init_app(self.app_b)

    def test_free_functions(self):
        with self.app_a.test_request_context():
            self.assertEqual(ugettext('Large'), 'Large')
        with self.app_b.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')

    def test_methods(self):
        with self.app_a.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Large')
        with self.app_b.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Groß')
