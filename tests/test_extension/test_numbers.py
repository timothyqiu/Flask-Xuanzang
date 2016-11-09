from __future__ import unicode_literals

from decimal import Decimal

from flask_xuanzang import Xuanzang, NumberFormatError
from flask_xuanzang import format_decimal
from mock import Mock

from tests import XuanzangTestCase


class NumbersTestCase(XuanzangTestCase):
    DEFAULT_LOCALE = None

    def setUp(self):
        self.app = self.create_app(self.DEFAULT_LOCALE)
        self.locale_selector = Mock(name='locale_selector', return_value=None)
        self.xuanzang = Xuanzang(self.app,
                                 locale_selector=self.locale_selector)


class FormatDecimalMethodTestCase(NumbersTestCase):
    DEFAULT_LOCALE = 'de'

    def test_need_app_context(self):
        self.assertRaises(RuntimeError, self.xuanzang.format_decimal, 1234567)

    def test_format_int(self):
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.format_decimal(1234567),
                             '1.234.567')

    def test_format_float(self):
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.format_decimal(1234567.89),
                             '1.234.567,89')

    def test_format_decimal(self):
        with self.app.test_request_context():
            self.assertEqual(self.xuanzang.format_decimal(Decimal(1234567)),
                             '1.234.567')


class FormatDecimalFunctionTestCase(NumbersTestCase):
    DEFAULT_LOCALE = 'de'

    def test_need_app_context(self):
        self.assertRaises(RuntimeError, format_decimal, 1234567)

    def test_format_int(self):
        with self.app.test_request_context():
            self.assertEqual(format_decimal(1234567), '1.234.567')

    def test_format_float(self):
        with self.app.test_request_context():
            self.assertEqual(format_decimal(1234567.89), '1.234.567,89')

    def test_format_decimal(self):
        with self.app.test_request_context():
            self.assertEqual(format_decimal(Decimal(1234567)), '1.234.567')


class ParseDecimalMethodTestCase(NumbersTestCase):
    DEFAULT_LOCALE = 'de'

    def test_need_app_context(self):
        self.assertRaises(RuntimeError,
                          self.xuanzang.parse_decimal, '1.234.567')

    def test_parse_failure(self):
        with self.app.test_request_context():
            self.assertRaises(NumberFormatError,
                              self.xuanzang.parse_decimal, 'abc')

    def test_parse_int(self):
        with self.app.test_request_context():
            # with decimal separator
            self.assertEqual(self.xuanzang.parse_decimal('1.234.567'),
                             Decimal(1234567))
            # without decimal separator
            self.assertEqual(self.xuanzang.parse_decimal('1234567'),
                             Decimal('1234567'))

    def test_parse_float(self):
        with self.app.test_request_context():
            # with decimal separator
            self.assertEqual(self.xuanzang.parse_decimal('1.234.567,89'),
                             Decimal('1234567.89'))
            # without decimal separator
            self.assertEqual(self.xuanzang.parse_decimal('1234567,89'),
                             Decimal('1234567.89'))
