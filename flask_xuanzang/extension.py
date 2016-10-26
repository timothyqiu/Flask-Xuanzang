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
        return Translations.load(directory, locales)


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


def ugettext(message, **variables):
    attan = Xuanzang.get_attan()
    return attan.ugettext(message, **variables)


def ungettext(singular, plural, num, **variables):
    attan = Xuanzang.get_attan()
    return attan.ungettext(singular, plural, num, **variables)
