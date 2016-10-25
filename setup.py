from setuptools import setup

import flask_xuanzang


with open('README.rst') as f:
    readme = f.read()

setup(
    name='Flask-Xuanzang',
    version=flask_xuanzang.__version__,
    description='Implements i18n and l10n support for Flask.',
    long_description=readme,
    url='https://github.com/timothyqiu/Flask-Xuanzang',
    author='Timothy Qiu',
    author_email='timothyqiu32@gmail.com',
    license='MIT',
    packages=['flask_xuanzang'],
    install_requires=[
        'Flask>=0.9',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
