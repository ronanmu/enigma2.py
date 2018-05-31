"""
tests.test_api
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests the api

Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""
# pylint: disable=protected-access
import os, sys
import unittest
import requests_mock
from tests.sample_responses import (SAMPLE_ABOUT, SAMPLE_STATUS_INFO, SAMPLE_VOL13_RESPONSE, SAMPLE_POWER_RESPONSE,
                                    SAMPLE_MUTE_RESPONSE, SAMPLE_CHANNEL_CHANGE_RESPONSE, SAMPLE_STANDBY_STATUS_INFO,
                                    SAMPLE_EMPTY_EPG_SEARCH, SAMPLE_EMPTY_TIMER_LIST)

import enigma2.api
from enigma2.error import Enigma2Error


class TestAPI(unittest.TestCase):
    """ Tests enigma2.api module. """

    def _update_test_mock(self, m):
        m.register_uri('GET', '/api/statusinfo', json=SAMPLE_STATUS_INFO, status_code=200)

    def test_empty_create(self):
        """Testing error raised on no connection details provided"""
        self.assertTrue(Enigma2Error, lambda: enigma2.api.Enigma2Connection)

    def test_connection_failure(self):
        """Testing error raised when non-existent server provided"""
        self.assertTrue(Enigma2Error, lambda: enigma2.api.Enigma2Connection(host='1.1.1.1'))

    @requests_mock.mock()
    def test_create(self, m):
        """ Test creating a new device. """
        self._update_test_mock(m)
        # Random local device
        self.assertTrue(enigma2.api.Enigma2Connection(host='123.123.123.123'))

    @requests_mock.mock()
    def test_unauthorized(self, m):
        """Test that unauth messsage is reported correctly"""
        m.register_uri('GET', '/api/statusinfo', status_code=401)

        self.assertTrue(Enigma2Error, lambda : enigma2.api.Enigma2Connection(
            host='123.123.123.123', username='test', password='123'))

    @requests_mock.mock()
    def test_raise_404(self, m):
        """Test that a 404 is raised for some reason"""
        m.register_uri('GET', '/api/statusinfo', status_code=404)

        self.assertTrue(Enigma2Error, lambda : enigma2.api.Enigma2Connection(host='123.123.123.123'))

    # @requests_mock.mock()
    # def test_raise_500(self, m):
    #     """Test that a 500 error is managed correctly"""
    #     from requests.exceptions import ReadTimeout
    #
    #     m.register_uri('GET', '/api/statusinfo', status_code=500, body=ReadTimeout('test error'))
    #
    #     device = enigma2.api.Enigma2Connection(host='123.123.123.123')


    @requests_mock.mock()
    def test_playback_type(self, m):
        """Check the playback type"""
        self._update_test_mock(m)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        playback_type = device.get_current_playback_type()
        self.assertIs(enigma2.api.PlaybackType.live, playback_type)

    @requests_mock.mock()
    def test_about(self, m):
        """ Testing the about response"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/about', json=SAMPLE_ABOUT, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123', is_https=True)
        about = device.get_about()
        self.assertEqual('Mock', about['brand'])

    @requests_mock.mock()
    def test_mute(self, m):
        """Testing the mute response"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/vol?set=mute', json=SAMPLE_MUTE_RESPONSE, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.toggle_mute()
        self.assertTrue(status)

    @requests_mock.mock()
    def test_channel_up_down(self, m):
        """Testing channel up and down requests"""
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
        """Testing all the setting/up/down volume"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/vol?set=set13', json=SAMPLE_VOL13_RESPONSE, status_code=200)
        m.register_uri('GET', '/api/vol?set=up', json=SAMPLE_VOL13_RESPONSE, status_code=200)
        m.register_uri('GET', '/api/vol?set=down', json=SAMPLE_VOL13_RESPONSE, status_code=200)
        m.register_uri('GET', '/api/vol?set=set1000', exc=Enigma2Error)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        self.assertTrue(device.set_volume(13))
        self.assertTrue(device.volume_down())
        self.assertTrue(device.volume_up())
        self.assertTrue(Enigma2Error, lambda: device.set_volume(1000))


    @requests_mock.mock()
    def test_toggle_standby(self, m):
        """Test toggle standby"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/powerstate?newstate=0', json=SAMPLE_POWER_RESPONSE, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.toggle_standby()
        self.assertTrue(status)

    @requests_mock.mock()
    def test_standby_status(self, m):
        """Test standby status info"""
        m.register_uri('GET', '/api/statusinfo', json=SAMPLE_STANDBY_STATUS_INFO, status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123', port=1234)
        status_info = device.get_status_info()
        self.assertTrue(status_info['inStandby'])
        self.assertTrue(device.is_box_in_standby())

        status = device.refresh_status_info()
        self.assertTrue(status_info['inStandby'])
        self.assertTrue(device.is_box_in_standby())

        url = device.get_current_playing_picon_url()
        self.assertIs(None, url)

        playback_type = device.get_current_playback_type()
        self.assertIs(enigma2.api.PlaybackType.none, playback_type)

    @requests_mock.mock()
    def test_status(self, m):
        """Testing getting the status"""
        self._update_test_mock(m)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        status = device.get_status_info()
        self.assertFalse(status['inStandby'])
        self.assertFalse(device.is_box_in_standby())
        self.assertEqual('ITV2', status['currservice_station'])

        status = device.refresh_status_info()
        self.assertFalse(status['inStandby'])
        self.assertFalse(device.is_box_in_standby())

    @requests_mock.mock()
    def test_get_picon(self, m):
        """Test locate the picon"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/statusinfo', json=SAMPLE_STATUS_INFO, status_code=200)
        m.register_uri('HEAD', '/picon/itv2.png', status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        url = device.get_current_playing_picon_url()
        self.assertEqual('http://123.123.123.123/picon/itv2.png', url)


    @requests_mock.mock()
    def test_load_sources(self, m):
        """Testing parsing the source services JSON"""
        self._update_test_mock(m)
        with open(self._file_path('getallservices.json')) as json_file:
            m.register_uri('GET', '/api/getallservices', text=json_file.read(), status_code=200)

        device = enigma2.api.Enigma2Connection(url='https://123.123.123.123', port=2300)
        services = device.load_services()
        self.assertIsNotNone(services)

        services = device.load_services(bouquet_name='Children')
        self.assertIsNotNone(services)
        self.assertEqual(10, len(services))

        services = device.load_services(bouquet_name='Does not exist')
        self.assertIsNotNone(services)

    @requests_mock.mock()
    def test_search_epg(self, m):
        """Testing searching the EPG"""
        self._update_test_mock(m)
        m.register_uri('GET', '/api/epgsearch?search=werwe', json=SAMPLE_EMPTY_EPG_SEARCH, status_code=200)
        with open(self._file_path('epgsearch_home_and_away.json')) as json_file:
            m.register_uri('GET', '/api/epgsearch?search=Home%20and%20Away', text=json_file.read(), status_code=200)

        device = enigma2.api.Enigma2Connection(host='123.123.123.123')
        epg_results = device.search_epg('Home and Away')
        self.assertIsNotNone(epg_results)
        self.assertEqual(44, len(epg_results))

        first_result = epg_results[0]
        self.assertEqual(29231, first_result['id'])
        self.assertEqual(25, first_result['duration'])
        self.assertEqual('1:0:1:1E24:809:2:11A0000:0:0:0:', first_result['sref'])

        epg_results = device.search_epg('werwe')
        self.assertIs(0, len(epg_results))


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

    @staticmethod
    def _file_path(file_name):
        thispath = os.path.dirname(__file__)
        return "{}/{}".format(thispath, file_name)

