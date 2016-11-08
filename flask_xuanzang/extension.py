from __future__ import absolute_import
from __future__ import unicode_literals

import functools
import os

from babel.support import LazyProxy, Locale, Translations
from flask import current_app
from flask import _app_ctx_stack


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
    LOCALE_CACHE_KEY = 'xuanzang_locale'

    def __init__(self, translation_directory,
                 default_locale, locale_selector):
        self.translation_directory = translation_directory
        self.default_locale = Locale.parse(default_locale)
        self.locale_selector = locale_selector
        self.translation_cache = {}

    def _get_cache_object(self):
        context = _app_ctx_stack.top
        if not context:
            raise RuntimeError('No application context')
        return context

    def _get_locale(self):
        if not self.locale_selector:
            return self.default_locale
        raw_locale = self.locale_selector()
        if raw_locale is None:
            return self.default_locale
        return Locale.parse(raw_locale)

    def _load_translations(self, locale):
        directory = self.translation_directory
        translations = Translations.load(directory, [locale])
        translations.set_output_charset('utf-8')
        return translations

    def load_translations(self, locale):
        translations = self.translation_cache.get(locale)
        if not translations:
            translations = self._load_translations(locale)
            self.translation_cache[locale] = translations
        return translations

    def get_locale(self):
        obj = self._get_cache_object()
        locale = getattr(obj, self.LOCALE_CACHE_KEY, None)
        if not locale:
            locale = self._get_locale()
            setattr(obj, self.LOCALE_CACHE_KEY, locale)
        return locale

    def get_translations(self):
        locale = self.get_locale()
        return self.load_translations(locale)

    def refresh(self):
        obj = self._get_cache_object()
        if hasattr(obj, self.LOCALE_CACHE_KEY):
            delattr(obj, self.LOCALE_CACHE_KEY)

    def refresh_translations(self):
        self.translation_cache = {}


class Xuanzang(ShoshinMixin):
    """Central controller class that can be used to configure how
    Flask-Xuanzang behaves.

    :param app: Flask instance
    :param locale_selector: A callback function for locale selection
    """

    EXTENSION_KEY = 'xuanzang'

    def __init__(self, app=None, locale_selector=None):
        self.locale_selector = locale_selector

        if app:
            self.init_app(app, locale_selector=locale_selector)

    def init_app(self, app, locale_selector=None):
        """Initialzes an application for the use with this setup."""
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

    def refresh(self):
        """Refreshes the cached locale information."""
        return self.get_attan().refresh()

    def refresh_translations(self):
        """Refreshes the cached translations."""
        return self.get_attan().refresh_translations()


def _translate(function_name, *args, **kwargs):
    attan = Xuanzang.get_attan()
    return getattr(attan, function_name)(*args, **kwargs)


def _lazy_translate(function_name, *args, **kwargs):
    func = functools.partial(_translate, function_name, *args, **kwargs)
    return LazyProxy(func, enable_cache=False)


def gettext(message, **variables):
    """Translates `message` and returns it in a UTF-8 bytestring.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    """
    return _translate('gettext', message, **variables)


def ngettext(singular, plural, num, **variables):
    """Translates `singular` and `plural` and returns the appropriate string
    based on `number` in a UTF-8 bytestring.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    """
    return _translate('ngettext', singular, plural, num, **variables)


def pgettext(context, message, **variables):
    """Translates `message` given the `context`"""
    return _translate('pgettext', context, message, **variables)


def npgettext(context, singular, plural, num, **variables):
    """Translates `singular` and `plural` and returns the appropriate string
    based on `number` and `context`.
    """
    return _translate('npgettext', context, singular, plural, num, **variables)


def ugettext(message, **variables):
    """Translates `message`."""
    return _translate('ugettext', message, **variables)


def ungettext(singular, plural, num, **variables):
    """Translates `singular` and `plural` and returns the appropriate string
    based on `number`.
    """
    return _translate('ungettext', singular, plural, num, **variables)


def lazy_gettext(message, **variables):
    """Like :func:`gettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('gettext', message, **variables)


def lazy_ngettext(singular, plural, num, **variables):
    """Like :func:`ngettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('ngettext', singular, plural, num, **variables)


def lazy_pgettext(context, message, **variables):
    """Like :func:`pgettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('pgettext', context, message, **variables)


def lazy_npgettext(context, singular, plural, num, **variables):
    """Like :func:`npgettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('npgettext',
                           context, singular, plural, num, **variables)


def lazy_ugettext(message, **variables):
    """Like :func:`ugettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('ugettext', message, **variables)


def lazy_ungettext(singular, plural, num, **variables):
    """Like :func:`ungettext` but the string returned is lazy. The translation
    happens when it is used as an actual string.
    """
    return _lazy_translate('ungettext', singular, plural, num, **variables)
