#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='recommendr',
    version='0.0.1a',
    description='Movie recommendation engine.',
    long_description=readme + '\n\n' + history,
    author='Chris Lawlor',
    author_email='lawlor.chris@gmail.com',
    url='https://github.com/chrislawlor/recommendr',
    packages=[
        'recommendr',
    ],
    package_dir={'recommendr': 'recommendr'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='recommendr',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    #test_suite='tests',
    cmdclass={'test': PyTest}
)
