from __future__ import absolute_import

from flask_xuanzang.extension import Xuanzang
from flask_xuanzang.extension import gettext, ngettext
from flask_xuanzang.extension import ugettext, ungettext
from flask_xuanzang.extension import pgettext, npgettext
from flask_xuanzang.extension import lazy_gettext, lazy_ngettext
from flask_xuanzang.extension import lazy_ugettext, lazy_ungettext
from flask_xuanzang.extension import lazy_pgettext, lazy_npgettext


__all__ = [
    'Xuanzang',
    'gettext', 'ngettext',
    'ugettext', 'ungettext',
    'pgettext', 'npgettext',
    'lazy_gettext', 'lazy_ngettext',
    'lazy_ugettext', 'lazy_ungettext',
    'lazy_pgettext', 'lazy_npgettext',
]

__version__ = '0.0.0'
