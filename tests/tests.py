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
from flask_xuanzang import ugettext, ungettext
from flask_xuanzang import pgettext, npgettext
from flask_xuanzang import lazy_gettext, lazy_ngettext
from flask_xuanzang import lazy_ugettext, lazy_ungettext
from flask_xuanzang import lazy_pgettext, lazy_npgettext


PY2 = (sys.version_info[0] == 2)


class XuanzangTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.check_call(['pybabel', '-q', 'compile', '-d',
                               os.path.join('tests', 'translations')])


class SingleAppTestCase(XuanzangTestCase):
    def setUp(self, default_locale='de', with_locale_selector=True):
        super(SingleAppTestCase, self).setUp()

        self.app = Flask(__name__)
        self.app.config['XUANZANG_DEFAULT_LOCALE'] = default_locale

        self.locale_selector = None
        if with_locale_selector:
            self.locale_selector = Mock(name='locale_selector',
                                        return_value=None)
        self.xuanzang = Xuanzang(self.app,
                                 locale_selector=self.locale_selector)


class GettextTestCase(SingleAppTestCase):
    def setUp(self):
        super(GettextTestCase, self).setUp(with_locale_selector=False)

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
        super(LocaleSelectorTestCase, self).setUp(
            default_locale='de',
            with_locale_selector=True)

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


class LazyGettextTestCase(SingleAppTestCase):
    def test_not_lazy(self):
        self.assertRaises(RuntimeError, gettext, 'Large')

    def test_lazy_gettext(self):
        message = lazy_gettext('Large')
        with self.app.test_request_context():
            if PY2:
                self.assertEqual(message, 'Groß'.encode('utf-8'))
            else:
                self.assertEqual(message, 'Groß')

    def test_lazy_ngettext(self):
        singular = lazy_ngettext('%(num)s apple', '%(num)s apples', 1)
        plural = lazy_ngettext('%(num)s apple', '%(num)s apples', 2)
        with self.app.test_request_context():
            if PY2:
                self.assertEqual(singular, '1 Apfel'.encode('utf-8'))
                self.assertEqual(plural, '2 Äpfel'.encode('utf-8'))
            else:
                self.assertEqual(singular, '1 Apfel')
                self.assertEqual(plural, '2 Äpfel')

    def test_lazy_ugettext(self):
        message = lazy_ugettext('Large')
        with self.app.test_request_context():
            self.assertEqual(message, 'Groß')

    def test_lazy_ungettext(self):
        singular = lazy_ungettext('%(num)s apple', '%(num)s apples', 1)
        plural = lazy_ungettext('%(num)s apple', '%(num)s apples', 2)
        with self.app.test_request_context():
            self.assertEqual(singular, '1 Apfel')
            self.assertEqual(plural, '2 Äpfel')

    def test_lazy_pgettext(self):
        message = lazy_pgettext('month name', 'May')
        with self.app.test_request_context():
            self.assertEqual(message, 'Mai')

    def test_lazy_npgettext(self):
        singular = lazy_npgettext('fruits', 'apple', 'apples', 1)
        plural = lazy_npgettext('fruits', 'apple', 'apples', 2)
        with self.app.test_request_context():
            self.assertEqual(singular, 'Apfel')
            self.assertEqual(plural, 'Äpfel')


class GettextLocaleCacheTestCase(SingleAppTestCase):
    def test_cache(self):
        with self.app.test_request_context():
            ugettext('Large')
            self.assertEqual(self.locale_selector.call_count, 1)

            ungettext('%(num)s apple', '%(num)s apples', 1)
            self.assertEqual(self.locale_selector.call_count, 1)

    def test_refresh(self):
        with self.app.test_request_context():
            ugettext('Large')
            self.xuanzang.refresh()
            ungettext('%(num)s apple', '%(num)s apples', 1)
            self.assertEqual(self.locale_selector.call_count, 2)

    def test_no_cache_between_requests(self):
        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(self.locale_selector.call_count, 1)

        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(self.locale_selector.call_count, 2)


class LazyGettextLocaleCacheTestCase(SingleAppTestCase):
    def test_cache(self):
        message = lazy_ugettext('Large')
        with self.app.test_request_context():
            len(message)  # Triggers loading
            self.assertEqual(self.locale_selector.call_count, 1)

            len(message)  # Triggers loading
            self.assertEqual(self.locale_selector.call_count, 1)

    def test_refresh_cache(self):
        message = lazy_ugettext('Large')
        with self.app.test_request_context():
            len(message)  # Triggers loading
            self.assertEqual(self.locale_selector.call_count, 1)

            self.xuanzang.refresh()

            len(message)  # Triggers loading
            self.assertEqual(self.locale_selector.call_count, 2)


class MethodTestCase(SingleAppTestCase):
    def test_gettext(self):
        self.locale_selector.return_value = None
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), 'Groß')

    def test_locale_selector(self):
        self.locale_selector.return_value = 'zh_CN'
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.ugettext('Large'), '大型')
            self.locale_selector.assert_any_call()

    def test_not_lazy(self):
        self.assertRaises(RuntimeError, self.xuanzang.gettext, 'Large')

    def test_lazy_gettext(self):
        message = self.xuanzang.lazy_gettext('Large')
        with self.app.test_request_context():
            if PY2:
                self.assertEqual(message, 'Groß'.encode('utf-8'))
            else:
                self.assertEqual(message, 'Groß')

    def test_lazy_ngettext(self):
        singular = self.xuanzang.lazy_ngettext('%(num)s apple',
                                               '%(num)s apples', 1)
        plural = self.xuanzang.lazy_ngettext('%(num)s apple',
                                             '%(num)s apples', 2)
        with self.app.test_request_context():
            if PY2:
                self.assertEqual(singular, '1 Apfel'.encode('utf-8'))
                self.assertEqual(plural, '2 Äpfel'.encode('utf-8'))
            else:
                self.assertEqual(singular, '1 Apfel')
                self.assertEqual(plural, '2 Äpfel')

    def test_lazy_ugettext(self):
        message = self.xuanzang.lazy_ugettext('Large')
        with self.app.test_request_context():
            self.assertEqual(message, 'Groß')

    def test_lazy_ungettext(self):
        singular = self.xuanzang.lazy_ungettext('%(num)s apple',
                                                '%(num)s apples', 1)
        plural = self.xuanzang.lazy_ungettext('%(num)s apple',
                                              '%(num)s apples', 2)
        with self.app.test_request_context():
            self.assertEqual(singular, '1 Apfel')
            self.assertEqual(plural, '2 Äpfel')

    def test_lazy_pgettext(self):
        message = self.xuanzang.lazy_pgettext('month name', 'May')
        with self.app.test_request_context():
            self.assertEqual(message, 'Mai')

    def test_lazy_npgettext(self):
        singular = self.xuanzang.lazy_npgettext('fruits', 'apple', 'apples', 1)
        plural = self.xuanzang.lazy_npgettext('fruits', 'apple', 'apples', 2)
        with self.app.test_request_context():
            self.assertEqual(singular, 'Apfel')
            self.assertEqual(plural, 'Äpfel')


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
