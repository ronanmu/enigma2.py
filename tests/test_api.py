"""
tests.test_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the api

Copyright (c) 2017 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""
# pylint: disable=protected-access
import unittest

import enigma2.api
from enigma2.error import OpenWebIfError, MissingParamError


class TestAPI(unittest.TestCase):
    """ Tests enigma2.api module. """

    def test_create(self):
        """ Test creating a new device. """
        # Bogus config
        self.assertRaises(MissingParamError, lambda: openwebif.api.CreateDevice())
        self.assertRaises(OpenWebIfError, lambda: openwebif.api.CreateDevice('10.10.10.4'))

    def test_get_picon_name(self):
        self.assertEqual(enigma2.api.CreateDevice.get_picon_name('RTÉ One'), "rteone")

            # def test_status(self):
    #     """ Test getting version and status. """
    #     # So bad. Using a publically accessible box.
    #     client = openwebif.api.CreateDevice('public_box_on_web.com')
    #     self.assertEqual("OWIF 0.1.3", client.get_version())
    #     self.assertTrue(len(client.get_status_info()) > 8)

    #     # Test that an exception doesnt get thrown
    #     result = client.is_box_in_standby()
    #     self.assertTrue(result is True or result is False)
