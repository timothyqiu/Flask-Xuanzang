# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from babel.support import Locale
from mock import Mock, patch

from flask_xuanzang import Xuanzang
from flask_xuanzang import gettext, ngettext
from flask_xuanzang import ugettext, ungettext
from flask_xuanzang import pgettext, npgettext
from flask_xuanzang import lazy_gettext, lazy_ngettext
from flask_xuanzang import lazy_ugettext, lazy_ungettext
from flask_xuanzang import lazy_pgettext, lazy_npgettext

from tests import XuanzangTestCase


PY2 = (sys.version_info[0] == 2)


class GettextTestCase(XuanzangTestCase):
    DEFAULT_LOCALE = None

    def setUp(self):
        self.app = self.create_app(self.DEFAULT_LOCALE)
        self.locale_selector = Mock(name='locale_selector', return_value=None)
        self.xuanzang = Xuanzang(self.app,
                                 locale_selector=self.locale_selector)


class GettextFunctionTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

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


class LocaleSelectorTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

    def test_return_none(self):
        # Returning None selects the default locale
        self.locale_selector.return_value = None
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), 'Groß')
            self.locale_selector.assert_any_call()

    def test_return_locale(self):
        # Returning Locale selects that locale
        self.locale_selector.return_value = Locale.parse('zh_CN')
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), '大型')
            self.locale_selector.assert_any_call()

    def test_return_text(self):
        # Returning text selects locale denoted by the text
        self.locale_selector.return_value = 'zh_CN'
        with self.app.test_request_context():
            self.assertEqual(ugettext('Large'), '大型')
            self.locale_selector.assert_any_call()

    def test_cache_in_request(self):
        # Result of locale selector is cached within the request by default
        with self.app.test_request_context():
            ugettext('Large')
            self.assertEqual(self.locale_selector.call_count, 1)

            ungettext('%(num)s apple', '%(num)s apples', 1)
            self.assertEqual(self.locale_selector.call_count, 1)

            ugettext('Large')
            self.assertEqual(self.locale_selector.call_count, 1)

    def test_no_cache_between_requests(self):
        # Result of locale selector is not cached between requests
        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(self.locale_selector.call_count, 1)

        with self.app.test_request_context():
            ungettext('%(num)s apple', '%(num)s apples', 1)
        self.assertEqual(self.locale_selector.call_count, 2)

        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(self.locale_selector.call_count, 3)

    def test_refresh(self):
        # Calling refresh() clears the cache
        with self.app.test_request_context():
            ugettext('Large')
            self.assertEqual(self.locale_selector.call_count, 1)

            self.xuanzang.refresh()
            ungettext('%(num)s apple', '%(num)s apples', 1)
            self.assertEqual(self.locale_selector.call_count, 2)

            self.xuanzang.refresh()
            ugettext('Large')
            self.assertEqual(self.locale_selector.call_count, 3)


@patch('babel.support.Translations.load')
class GetTranslationCacheTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

    def test_cache(self, mock_load):
        # Translation loading is cached for the each locale
        with self.app.test_request_context():
            # The cache is empty, always load from disk
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 1)

            # Locale is not changed, load from cache
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 1)

            # The new locale is not cached
            self.xuanzang.refresh()  # Clears locale selector cache
            self.locale_selector.return_value = 'zh_CN'
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 2)

            # The previous locale is still cached
            self.xuanzang.refresh()  # Clears locale selector cache
            self.locale_selector.return_value = 'de'
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 2)

            # The new locale is still cached
            self.xuanzang.refresh()  # Clears locale selector cache
            self.locale_selector.return_value = 'zh_CN'
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 2)

    def test_cache_between_requests(self, mock_load):
        # Translation loading is cached across requests
        # Requests have no means to affect translations for a specified locale

        # The cache is empty, always load from disk
        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 1)

        # Locale is not changed, load form cache
        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 1)

        # The new locale is not cached
        with self.app.test_request_context():
            self.locale_selector.return_value = 'zh_CN'
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 2)

        # The previous locale is still cached
        with self.app.test_request_context():
            self.locale_selector.return_value = 'de'
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 2)

        # The new locale is still cached
        with self.app.test_request_context():
            self.locale_selector.return_value = 'zh_CN'
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 2)

    def test_clear_cache_in_request(self, mock_load):
        # refresh_translations() clears translation cache in request
        with self.app.test_request_context():
            ugettext('Large')
            self.assertEqual(mock_load.call_count, 1)

            self.xuanzang.refresh_translations()

            ugettext('Large')
            self.assertEqual(mock_load.call_count, 2)

    def test_clear_cache_between_requests(self, mock_load):
        # refresh_translations() clears translation cache between requests

        with self.app.test_request_context():
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 1)

        with self.app.test_request_context():
            self.xuanzang.refresh_translations()  # Application Context needed
            ugettext('Large')
        self.assertEqual(mock_load.call_count, 2)


class LazyGettextTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

    def test_not_lazy(self):
        # not-lazy gettext should be called inside application context
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


class LazyGettextLocaleCacheTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

    def test_cache(self):
        message = lazy_ugettext('Large')
        with self.app.test_request_context():
            len(message)  # Triggers ugettext
            self.assertEqual(self.locale_selector.call_count, 1)

            len(message)  # Triggers ugettext
            self.assertEqual(self.locale_selector.call_count, 1)

    def test_refresh_cache(self):
        message = lazy_ugettext('Large')
        with self.app.test_request_context():
            len(message)  # Triggers ugettext
            self.assertEqual(self.locale_selector.call_count, 1)

            self.xuanzang.refresh()

            len(message)  # Triggers ugettext
            self.assertEqual(self.locale_selector.call_count, 2)


class MethodTestCase(GettextTestCase):
    DEFAULT_LOCALE = 'de'

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
