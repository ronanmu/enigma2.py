"""
tests.test_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the api

Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""
# pylint: disable=protected-access
import unittest
import requests_mock
from tests.sample_responses import (SAMPLE_ABOUT, SAMPLE_STATUS_INFO, SAMPLE_VOL13_RESPONSE, SAMPLE_POWER_RESPONSE,
                                    SAMPLE_MUTE_RESPONSE, SAMPLE_CHANNEL_CHANGE_RESPONSE)

import enigma2.api
from enigma2.error import Enigma2Error, MissingParamError


class TestAPI(unittest.TestCase):
    """ Tests enigma2.api module. """

    def _update_test_mock(self, m):
        m.register_uri('GET', '/api/statusinfo', json=SAMPLE_STATUS_INFO, status_code=200)

    def test_empty_create(self):
        self.assertTrue(MissingParamError, lambda: enigma2.api.Enigma2Connection)

    @requests_mock.mock()
    def test_create(self, m):
        """ Test creating a new device. """

        self._update_test_mock(m)
        # Random local device
        self.assertTrue(enigma2.api.Enigma2Connection(host='123.123.123.123'))

    @requests_mock.mock()
    def test_about(self, m):
        """ Testing the about response"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/about', json=SAMPLE_ABOUT, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        about = device.get_about()
        self.assertEqual('Mock', about['brand'])

    @requests_mock.mock()
    def test_mute(self, m):
        """Testing the mute response"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/vol?set=mute', json=SAMPLE_MUTE_RESPONSE, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.mute_volume()
        self.assertTrue(status)

    @requests_mock.mock()
    def test_channel_up_down(self, m):
        self._update_test_mock(m)
        m.register_uri('GET', '/api/remotecontrol?command=402', json=SAMPLE_CHANNEL_CHANGE_RESPONSE, status_code=200)
        m.register_uri('GET', '/api/remotecontrol?command=403', json=SAMPLE_CHANNEL_CHANGE_RESPONSE, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.channel_up()
        self.assertTrue(status)
        status = device.channel_down()
        self.assertTrue(status)


    @requests_mock.mock()
    def test_set_vol(self, m):
        self._update_test_mock(m)
        m.register_uri('GET', '/api/vol?set=set13', json=SAMPLE_VOL13_RESPONSE, status_code=200)
        m.register_uri('GET', '/api/vol?set=set1000', exc=Enigma2Error)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.set_volume(13)
        self.assertTrue(status)
        self.assertTrue(Enigma2Error, lambda: device.set_volume(1000))


    @requests_mock.mock()
    def test_toggle_standby(self, m):
        self._update_test_mock(m)
        m.register_uri('GET', '/api/powerstate?newstate=0', json=SAMPLE_POWER_RESPONSE, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.toggle_standby()
        self.assertTrue(status)


    @requests_mock.mock()
    def test_status(self, m):
        self._update_test_mock(m)
        m.register_uri('GET', '/api/statusinfo', json=SAMPLE_STATUS_INFO, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.get_status_info()
        self.assertFalse(status['inStandby'])
        self.assertFalse(device.is_box_in_standby())
        self.assertEqual('ITV2', status['currservice_station'])

        status = device.refresh_status_info()
        self.assertFalse(status['inStandby'])
        self.assertFalse(device.is_box_in_standby())

  #  def test_get_picon_name(self):
   #     self.assertEqual(enigma2.api.Engima2Device.get_picon_name('RTÉ One'), "rteone")

            # def test_status(self):
    #     """ Test getting version and status. """
    #     # So bad. Using a publically accessible box.
    #     client = openwebif.api.CreateDevice('public_box_on_web.com')
    #     self.assertEqual("OWIF 0.1.3", client.get_version())
    #     self.assertTrue(len(client.get_status_info()) > 8)

    #     # Test that an exception doesnt get thrown
    #     result = client.is_box_in_standby()
    #     self.assertTrue(result is True or result is False)

