# Copyright (C) 2021 Flowdas Inc. & Dong-gweon Oh <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages

setup_requires = [
]

install_requires = [
]

tests_require = [
    'pytest',
    'pytest-cov',
    'tox',
]

dev_requires = tests_require + [
]

setup(
    name='typeable',
    version=open('VERSION').read().strip(),
    url='https://github.com/flowdas/typeable',
    description='A platform-agnostic library for schema modeling, validation and conversion',
    author='Flowdas Inc.',
    author_email='prospero@flowdas.com',
    packages=[
        'typeable',
    ],
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'dev': dev_requires,
    },
    scripts=[],
    entry_points={},
    zip_safe=True,
    keywords=('validation', 'modeling', 'schema', 'typing'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
