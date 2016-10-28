from __future__ import absolute_import
from __future__ import unicode_literals

import os

from babel.support import Locale, Translations
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


class Attan(ShoshinMixin):
    def __init__(self, translation_directory, default_locale):
        self.translation_directory = translation_directory
        self.default_locale = Locale.parse(default_locale)

    def get_locale(self):
        return self.default_locale

    def get_translations(self):
        directory = self.translation_directory
        locales = [self.get_locale()]
        translations = Translations.load(directory, locales)
        translations.set_output_charset('utf-8')
        return translations


class Xuanzang(ShoshinMixin):
    EXTENSION_KEY = 'xuanzang'

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.extensions = getattr(app, 'extensions', {})
        app.extensions[self.EXTENSION_KEY] = self.init_attan(app)

    def init_attan(self, app):
        directory = app.config.get('XUANZANG_TRANSLATION_DIRECTORY',
                                   'translations')
        if not os.path.isabs(directory):
            directory = os.path.join(app.root_path, directory)

        return Attan(
            directory,
            app.config.get('XUANZANG_DEFAULT_LOCALE', 'en'),
        )

    @classmethod
    def get_attan(cls):
        return current_app.extensions[cls.EXTENSION_KEY]

    def get_locale(self):
        return self.get_attan().get_locale()

    def get_translations(self):
        return self.get_attan().get_translations()


def _do_translation(function_name, *args, **kwargs):
    attan = Xuanzang.get_attan()
    return getattr(attan, function_name)(*args, **kwargs)


def gettext(message, **variables):
    '''Returns a string of the translation of the message.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    '''
    return _do_translation('gettext', message, **variables)


def ngettext(singular, plural, num, **variables):
    '''Returns a string of the translation of the singular or plural based on
    the number.

    :returns: a string on Python 3 and an UTF-8-encoded bytestring on Python 2
    '''
    return _do_translation('ngettext', singular, plural, num, **variables)


def pgettext(context, message, **variables):
    return _do_translation('pgettext', context, message, **variables)


def npgettext(context, singular, plural, num, **variables):
    return _do_translation('npgettext',
                           context, singular, plural, num, **variables)


def ugettext(message, **variables):
    return _do_translation('ugettext', message, **variables)


def ungettext(singular, plural, num, **variables):
    return _do_translation('ungettext', singular, plural, num, **variables)
