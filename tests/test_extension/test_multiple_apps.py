# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from mock import Mock

from flask_xuanzang import Xuanzang
from flask_xuanzang import ugettext

from tests import XuanzangTestCase


class MultipleAppsTestCase(XuanzangTestCase):
    def setUp(self):
        self.xuanzang = Xuanzang()

        self.app_a = self.create_app('en')
        self.locale_selector_a = Mock(name='locale_selector_a',
                                      return_value=None)
        self.xuanzang.init_app(self.app_a,
                               locale_selector=self.locale_selector_a)

        self.app_b = self.create_app('de')
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
