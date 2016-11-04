from __future__ import unicode_literals

import os
import shutil
import tempfile
import unittest

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from flask import Flask


# Like `pybabel compile`, but puts mo files in a specified directory
def _compile_catalog(domain, directory, output_directory):
    po_files = []
    mo_files = []
    for locale in os.listdir(directory):
        po_file = os.path.join(directory, locale,
                               'LC_MESSAGES', domain + '.po')
        if os.path.exists(po_file):
            po_files.append((locale, po_file))
            mo_files.append(os.path.join(output_directory, locale,
                                         'LC_MESSAGES', domain + '.mo'))

    for mo_file, (locale, po_file) in zip(mo_files, po_files):
        with open(po_file, 'rb') as f:
            catalog = read_po(f, locale)

        mo_dir = os.path.dirname(mo_file)
        if not os.path.exists(mo_dir):
            os.makedirs(mo_dir)

        with open(mo_file, 'wb') as f:
            write_mo(f, catalog)


class XuanzangTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Make sure mo files are generated
        cls.po_directory = os.path.join(os.path.dirname(__file__),
                                        'translations')
        cls.mo_directory = tempfile.mkdtemp()
        _compile_catalog('messages', cls.po_directory, cls.mo_directory)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.mo_directory)

    def create_app(self, default_locale):
        app = Flask(__name__)
        app.config.update({
            'TESTING': True,
            'XUANZANG_DEFAULT_LOCALE': default_locale,
            'XUANZANG_TRANSLATION_DIRECTORY': self.mo_directory,
        })
        return app
