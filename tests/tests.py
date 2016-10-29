# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import subprocess
import sys
import unittest

from flask import Flask
from mock import Mock

from flask_xuanzang import Xuanzang
from flask_xuanzang import gettext, ngettext
from flask_xuanzang import ugettext, ungettext, pgettext, npgettext


PY2 = (sys.version_info[0] == 2)


class XuanzangTestCase(unittest.TestCase):
    def setUp(self):
        subprocess.check_call(['pybabel', '-q', 'compile', '-d',
                               os.path.join('tests', 'translations')])


class SingleAppTestCase(XuanzangTestCase):
    def setUp(self, default_locale='de', locale_selector=None):
        super(SingleAppTestCase, self).setUp()

        self.app = Flask(__name__)
        self.app.config['XUANZANG_DEFAULT_LOCALE'] = default_locale
        self.xuanzang = Xuanzang(self.app, locale_selector=locale_selector)


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


class LocaleSelectorTestCase(SingleAppTestCase):
    def setUp(self):
        self.locale_selector = Mock(name='locale_selector')
        super(LocaleSelectorTestCase, self).setUp(
            default_locale='de',
            locale_selector=self.locale_selector)

    def test_return_none(self):
        self.locale_selector.return_value = None
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')
            self.locale_selector.assert_any_call()

    def test_return_locale(self):
        self.locale_selector.return_value = 'zh_CN'
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), '大型')
            self.locale_selector.assert_any_call()


class MethodTestCase(SingleAppTestCase):
    def setUp(self):
        self.locale_selector = Mock(name='locale_selector')
        super(MethodTestCase, self).setUp(locale_selector=self.locale_selector)

    def test_gettext(self):
        self.locale_selector.return_value = None
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Groß')

    def test_locale_selector(self):
        self.locale_selector.return_value = 'zh_CN'
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), '大型')
            self.locale_selector.assert_any_call()


class MultipleAppsTestCase(XuanzangTestCase):
    def setUp(self):
        super(MultipleAppsTestCase, self).setUp()

        self.xuanzang = Xuanzang()

        self.app_a = Flask(__name__)
        self.app_a.config['XUANZANG_DEFAULT_LOCALE'] = 'en'
        self.locale_selector_a = Mock(name='locale_selector_a',
                                      return_value=None)
        self.xuanzang.init_app(self.app_a,
                               locale_selector=self.locale_selector_a)

        self.app_b = Flask(__name__)
        self.app_b.config['XUANZANG_DEFAULT_LOCALE'] = 'de'
        self.locale_selector_b = Mock(name='locale_selector_b',
                                      return_value=None)
        self.xuanzang.init_app(self.app_b,
                               locale_selector=self.locale_selector_b)


class MultipleAppsFreeFunctionTestCase(MultipleAppsTestCase):
    def test_gettext(self):
        with self.app_a.test_request_context():
            self.assertEqual(ugettext('Large'), 'Large')
        with self.app_b.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')

    def test_locale_selector(self):
        self.locale_selector_a.return_value = 'de'
        self.locale_selector_b.return_value = 'zh_CN'

        with self.app_a.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')
        with self.app_b.test_request_context():
            self.assertEqual(ugettext('Large'), '大型')


class MultipleAppsMethodTestCase(MultipleAppsTestCase):
    def test_gettext(self):
        with self.app_a.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Large')
        with self.app_b.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Groß')
