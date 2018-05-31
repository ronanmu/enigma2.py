# Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
# Licensed under the MIT license.

# Used this guide to create module
# http://peterdowns.com/posts/first-time-with-pypi.html

from distutils.core import setup

setup(
    name='enigma2.py',
    version='0.01',
    description='Provides a python interface to interact with an Engima2 set top box running OpenWebIf',
    author='Ronan Murray',
    author_email='ronanmu@users.noreply.github.com',
    url='https://github.com/ronanmu/enigma2.py',
    download_url = 'https://github.com/ronanmu/enigma2.py/tarball/0.01',
    keywords='enigma2 openwebif python cgi interface',
    packages=['enigma2'],
    install_requires=['requests', 'jsonpath-rw'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet'
        ],
    )
