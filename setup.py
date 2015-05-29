# Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

# Used this guide to create module
# http://peterdowns.com/posts/first-time-with-pypi.html

from distutils.core import setup

setup(
    name='openwebif.py',
    version='0.2',
    description='Provides a python interface to interact with a device running OpenWebIf',
    author='Finbarr Brady',
    author_email='fbradyirl@users.noreply.github.com',
    url='https://github.com/fbradyirl/openwebif.py',
    download_url = 'https://github.com/fbradyirl/openwebif.py/tarball/0.2',
    keywords='enigma2 openwebif python cgi interface',
    packages=['openwebif'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet'
        ],
    )
