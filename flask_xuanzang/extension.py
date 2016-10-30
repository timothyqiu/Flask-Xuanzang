from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import os

from babel.support import LazyProxy, Locale, Translations
from flask import current_app


class ShoshinMixin(object):
    def get_locale(self):
        raise NotImplementedError()

    def get_translations(self):
        raise NotImplementedError()

    def gettext(self, message, **variables):
        t = self.get_translations()
        s = t.gettext(message)
        return s if not variables else s % variables

    def ngettext(self, singular, plural, num, **variables):
        variables.setdefault('num', num)
        t = self.get_translations()
        s = t.ngettext(singular, plural, num)
        return s if not variables else s % variables

    def pgettext(self, context, message, **variables):
        t = self.get_translations()
        s = t.upgettext(context, message)
        return s if not variables else s % variables

    def npgettext(self, context, singular, plural, num, **variables):
        t = self.get_translations()
        s = t.unpgettext(context, singular, plural, num)
        return s if not variables else s % variables

    def ugettext(self, message, **variables):
        t = self.get_translations()
        s = t.ugettext(message)
        return s if not variables else s % variables

    def ungettext(self, singular, plural, num, **variables):
        variables.setdefault('num', num)
        t = self.get_translations()
        s = t.ungettext(singular, plural, num)
        return s if not variables else s % variables

    def lazy_gettext(self, message, **variables):
        func = functools.partial(self.gettext, message, **variables)
        return LazyProxy(func, enable_cache=False)

    def lazy_ngettext(self, singular, plural, num, **variables):
        func = functools.partial(self.ngettext,
                                 singular, plural, num, **variables)
        return LazyProxy(func, enable_cache=False)

    def lazy_pgettext(self, context, message, **variables):
        func = functools.partial(self.pgettext, context, message, **variables)
        return LazyProxy(func, enable_cache=False)

    def lazy_npgettext(self, context, singular, plural, num, **variables):
        func = functools.partial(self.npgettext,
                                 context, singular, plural, num, **variables)
        return LazyProxy(func, enable_cache=False)

    def lazy_ugettext(self, message, **variables):
        func = functools.partial(self.ugettext, message, **variables)
        return LazyProxy(func, enable_cache=False)

    def lazy_ungettext(self, singular, plural, num, **variables):
        func = functools.partial(self.ungettext,
                                 singular, plural, num, **variables)
        return LazyProxy(func, enable_cache=False)


class Attan(ShoshinMixin):
    def __init__(self, translation_directory,
                 default_locale, locale_selector):
        self.translation_directory = translation_directory
        self.default_locale = Locale.parse(default_locale)
        self.locale_selector = locale_selector

    def get_locale(self):
        if not self.locale_selector:
            return self.default_locale
        raw_locale = self.locale_selector()
        if raw_locale is None:
            return self.default_locale
        return Locale.parse(raw_locale)

    def get_translations(self):
        directory = self.translation_directory
        locales = [self.get_locale()]
        translations = Translations.load(directory, locales)
        translations.set_output_charset('utf-8')
        return translations


class Xuanzang(ShoshinMixin):
    EXTENSION_KEY = 'xuanzang'

    def __init__(self, app=None, locale_selector=None):
        self.locale_selector = locale_selector

        if app:
            self.init_app(app, locale_selector=locale_selector)

    def init_app(self, app, locale_selector=None):
        locale_selector = locale_selector or self.locale_selector
        attan = self.init_attan(app, locale_selector)

        app.extensions = getattr(app, 'extensions', {})
        app.extensions[self.EXTENSION_KEY] = attan

    def init_attan(self, app, locale_selector):
        directory = app.config.get('XUANZANG_TRANSLATION_DIRECTORY',
                                   'translations')
        if not os.path.isabs(directory):
            directory = os.path.join(app.root_path, directory)

        return Attan(
            directory,
            app.config.get('XUANZANG_DEFAULT_LOCALE', 'en'),
            locale_selector,
        )

    @classmethod
    def get_attan(cls):
        return current_app.extensions[cls.EXTENSION_KEY]

    def get_locale(self):
        return self.get_attan().get_locale()

    def get_translations(self):
        return self.get_attan().get_translations()


def _translate(function_name, *args, **kwargs):
    attan = Xuanzang.get_attan()
    return getattr(attan, function_name)(*args, **kwargs)


def _lazy_translate(function_name, *args, **kwargs):
    func = functools.partial(_translate, function_name, *args, **kwargs)
    return LazyProxy(func, enable_cache=False)


def gettext(message, **variables):
    '''Returns a string of the translation of the message.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    '''
    return _translate('gettext', message, **variables)


def ngettext(singular, plural, num, **variables):
    '''Returns a string of the translation of the singular or plural based on
    the number.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    '''
    return _translate('ngettext', singular, plural, num, **variables)


def pgettext(context, message, **variables):
    return _translate('pgettext', context, message, **variables)


def npgettext(context, singular, plural, num, **variables):
    return _translate('npgettext', context, singular, plural, num, **variables)


def ugettext(message, **variables):
    return _translate('ugettext', message, **variables)


def ungettext(singular, plural, num, **variables):
    return _translate('ungettext', singular, plural, num, **variables)


def lazy_gettext(message, **variables):
    return _lazy_translate('gettext', message, **variables)


def lazy_ngettext(singular, plural, num, **variables):
    return _lazy_translate('ngettext', singular, plural, num, **variables)


def lazy_pgettext(context, message, **variables):
    return _lazy_translate('pgettext', context, message, **variables)


def lazy_npgettext(context, singular, plural, num, **variables):
    return _lazy_translate('npgettext',
                           context, singular, plural, num, **variables)


def lazy_ugettext(message, **variables):
    return _lazy_translate('ugettext', message, **variables)


def lazy_ungettext(singular, plural, num, **variables):
    return _lazy_translate('ungettext', singular, plural, num, **variables)
