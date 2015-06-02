"""
tests.test_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the api

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""
# pylint: disable=protected-access
import unittest
import openwebif.api
from openwebif.error import OpenWebIfError, MissingParamError
from requests.exceptions import ConnectionError

class TestAPI(unittest.TestCase):
    """ Tests openwebif.api module. """

    def test_create(self):
        """ Test creating a new device. """
        # Bogus config
        self.assertRaises(MissingParamError, lambda: openwebif.api.CreateDevice())
        self.assertRaises(OpenWebIfError, lambda: openwebif.api.CreateDevice('10.10.10.4'))


    def test_status(self):
        """ Test getting version and status. """
        # So bad. Using a publically accessible box.
        client = openwebif.api.CreateDevice('cable-dynamic-87-245-115-154.shinternet.ch')
        self.assertEqual("OWIF 0.1.3", client.get_version())
        self.assertTrue(len(client.get_status_info()) > 8)

