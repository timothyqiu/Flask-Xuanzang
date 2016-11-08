.. Flask Xuánzàng documentation master file, created by
   sphinx-quickstart on Tue Nov  8 15:07:53 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask Xuánzàng
==============

Implements i18n and l10n support for Flask.


.. contents::
   :local:
   :backlinks: none


Configuration
-------------

**Flask-Xuanzang** is mainly configured through the standard Flask config API.
These are the available options:

==================================  ==========================================
``XUANZANG_TRANSLATION_DIRECTORY``  Directory where translations are loaded
                                    from. Default is ``'translations'``.
``XUANZANG_DEFAULT_LOCALE``         Default locale to use if locale is not
                                    specified by the callback function.
                                    Default is ``'en'``.
==================================  ==========================================


API Reference
-------------

.. module:: flask_xuanzang

.. autoclass:: Xuanzang
   :members: init_app, refresh, refresh_translations


Gettext Functions
`````````````````
.. autofunction:: ugettext
.. autofunction:: ungettext
.. autofunction:: pgettext
.. autofunction:: npgettext

.. autofunction:: lazy_ugettext
.. autofunction:: lazy_ungettext
.. autofunction:: lazy_pgettext
.. autofunction:: lazy_npgettext


Legacy Gettext Functions
````````````````````````
.. autofunction:: gettext
.. autofunction:: ngettext
.. autofunction:: lazy_gettext
.. autofunction:: lazy_ngettext
