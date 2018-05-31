"""
enigma2.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with Enigma2 powered set-top-box running OpenWebIf

Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""

import logging
import re
import unicodedata

from enum import Enum
import requests
from requests.exceptions import ConnectionError as ReConnError
from enigma2.error import Enigma2Error

_LOGGER = logging.getLogger(__name__)


class PlaybackType(Enum):
    """ Enum for Playback Type """
    live = 1
    recording = 2
    none = 3


# pylint: disable=too-many-arguments,line-too-long,logging-not-lazy


def build_url_base(host, port, is_https):
    """
    Make base of url based on config
    """
    base = "http"
    if is_https:
        base += 's'

    base += "://"
    base += host
    if port:
        base += ":"
        base += str(port)

    return base

def enable_logging():
    """ Setup the logging for home assistant. """
    logging.basicConfig(level=logging.INFO)


class Enigma2Connection(object):
    """
    Create a new Connection to an Enigma.
    """

    def __init__(self, url=None, host=None, port=None,
                 username=None, password=None, is_https=False,
                 timeout=5, verify_ssl=True, use_gzip=True):
        enable_logging()
        _LOGGER.debug("Initialising new Enigma2 OpenWebIF client")

        if host is None and url is None:
            _LOGGER.error('Missing Enigma2 host!')
            raise Enigma2Error('Connection to Enigma2 failed - please supply connection details')

        self._username = username
        self._password = password
        self._timeout = timeout
        self._use_gzip = use_gzip
        self._verify_ssl = verify_ssl
        self._in_standby = True

        # Assign a new Requests Session
        self._session = requests.Session()

        # Used to build a list of URLs which have been tested to exist
        # (for picons)
        self.cached_urls_which_exist = []

        # Now build base url
        if not url:
            self._base = build_url_base(host, port, is_https)
        else:
            self._base = url

        _LOGGER.debug("Going to probe device to test connection")
        self.get_status_info()
        _LOGGER.debug("Connected OK!")

    def set_volume(self, new_volume):
        """
        Sets the volume to the new value

        :param new_volume: int from 0-100
        :return: True if successful, false if there was a problem
        """
        from enigma2.constants import (URL_VOLUME, COMMAND_VOL_SET)

        if -1 > new_volume < 101:
            raise Enigma2Error('Volume must be between 0 and 100')

        cmd = '%s%s' % (COMMAND_VOL_SET, str(new_volume))
        return self._check_response_result(URL_VOLUME, {COMMAND_VOL_SET: cmd})

    def volume_up(self):
        """
        Returns True if command success
        :return:
        """
        from enigma2.constants import (URL_VOLUME, COMMAND_VOL_SET, COMMAND_VOL_UP)

        return self._check_response_result(URL_VOLUME, {COMMAND_VOL_SET: COMMAND_VOL_UP})

    def volume_down(self):
        """
        Returns True if command success
        :return:
        """
        from enigma2.constants import (URL_VOLUME, COMMAND_VOL_SET, COMMAND_VOL_DOWN)

        return self._check_response_result(URL_VOLUME, {COMMAND_VOL_SET: COMMAND_VOL_DOWN})

    def toggle_mute(self):
        """
        Send mute command
        """
        from enigma2.constants import (URL_VOLUME, COMMAND_VOL_SET, COMMAND_VOL_MUTE)

        return self._check_response_result(URL_VOLUME, {COMMAND_VOL_SET: COMMAND_VOL_MUTE})

    def toggle_standby(self):
        """
        Returns True if command success, else, False
        """
        from enigma2.constants import (URL_TOGGLE_STANDBY, PARAM_NEWSTATE)

        result = self._check_response_result(URL_TOGGLE_STANDBY, {PARAM_NEWSTATE: '0'})
        # Update standby
        self.get_status_info()
        return result

    def toggle_play_pause(self):
        """
        Send Play Pause command
        """
        from enigma2.constants import (URL_REMOTE_CONTROL,
                                       PARAM_COMMAND, COMMAND_RC_PLAY_PAUSE_TOGGLE)

        result = self._check_response_result(URL_REMOTE_CONTROL,
                                             {PARAM_COMMAND: COMMAND_RC_PLAY_PAUSE_TOGGLE})
        # Update info
        self.get_status_info()
        return result

    def channel_up(self):
        """
        Send channel up command
        """
        from enigma2.constants import (URL_REMOTE_CONTROL,
                                       PARAM_COMMAND, COMMAND_RC_CHANNEL_UP)

        return self._check_response_result(URL_REMOTE_CONTROL,
                                           {PARAM_COMMAND: COMMAND_RC_CHANNEL_UP})

    def channel_down(self):
        """
        Send channel down command
        """
        from enigma2.constants import (URL_REMOTE_CONTROL,
                                       PARAM_COMMAND, COMMAND_RC_CHANNEL_DOWN)

        return self._check_response_result(URL_REMOTE_CONTROL,
                                           {PARAM_COMMAND: COMMAND_RC_CHANNEL_DOWN})

    def is_box_in_standby(self):
        """
        Returns True if box is now in standby, else, False
        """
        return self._in_standby

    def get_about(self):
        """
        Returns ElementTree containing the result of <host>/web/about
        or if element_to_query is not None, the value of that element
        """
        from enigma2.constants import URL_ABOUT

        response = self._invoke_api(URL_ABOUT)
        response_json = response.json()
        output = {
            "webifver": response_json['info']['webifver'],
            "imagedistro": response_json['info']['imagedistro'],
            "brand": response_json['info']['brand'],
            "boxtype": response_json['info']['boxtype'],
            "uptime": response_json['info']['uptime']
        }
        return output

    def refresh_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """
        return self.get_status_info()

    def get_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """
        from enigma2.constants import URL_STATUS_INFO

        response = self._invoke_api(URL_STATUS_INFO)
        response_json = response.json()
        self._in_standby = response_json['inStandby']
        return response_json

    def search_epg(self, program_name):
        """
        Search the EPG for the supplied program name
        :param program_name: name of the program to search for
        :return:
        """
        from enigma2.constants import (URL_EPG_SEARCH, PARAM_SEARCH)

        response = self._invoke_api(URL_EPG_SEARCH, {PARAM_SEARCH: program_name})
        response_json = response.json()
        if response_json['result']:
            return response_json['events']

        return []

    def get_current_playback_type(self, currservice_serviceref=None):
        """
        Get the currservice_serviceref playing media type.

        :param currservice_serviceref: If you already know the
        currservice_serviceref pass it here, else it will be
        determined
        :return: PlaybackType.live or PlaybackType.recording
        """
        if currservice_serviceref is None:
            if self.is_box_in_standby():
                return PlaybackType.none

            status_info = self.get_status_info()
            if 'currservice_serviceref' in status_info:
                currservice_serviceref = status_info['currservice_serviceref']

        if currservice_serviceref.startswith('1:0:0'):
            # This is a recording, not a live channel
            return PlaybackType.recording

        return PlaybackType.live

    def get_current_playing_picon_url(self, channel_name=None,
                                      currservice_serviceref=None):
        """
        Return the URL to the picon image for the currently playing channel

        :param channel_name: If specified, it will base url on this channel
        name else, fetch latest from get_status_info()
        :param currservice_serviceref: The service_ref for the current service
        :return: The URL, or None if not available
        """
        from enigma2.constants import URL_LCD_4_LINUX

        cached_info = None
        if channel_name is None:
            cached_info = self.get_status_info()
            if 'currservice_station' in cached_info:
                channel_name = cached_info['currservice_station']
            else:
                _LOGGER.debug('No channel currently playing')
                return None

        if currservice_serviceref is None:
            if cached_info is None:
                cached_info = self.get_status_info()
            currservice_serviceref = cached_info['currservice_serviceref']

        if currservice_serviceref.startswith('1:0:0'):
            # This is a recording, not a live channel
            # and get picon based on that

            # As a fallback, send LCD4Linux image (if available)
            url = '%s%s' % (self._base, URL_LCD_4_LINUX)
            _LOGGER.debug('This is a recording, trying url: %s', url)

        else:
            picon_name = self.get_picon_name(channel_name)
            url = '%s/picon/%s.png' % (self._base, picon_name)

        if url in self.cached_urls_which_exist:
            _LOGGER.debug('picon url (already tested): %s', url)
            return url

        if self._url_exists(url):
            _LOGGER.debug('picon url: %s', url)
            return url

        # Last ditch attenpt. If channel ends in HD, lets try
        # and get non HD picon
        if channel_name.lower().endswith('hd'):
            channel_name = channel_name[:-2]
            _LOGGER.debug('Going to look for non HD picon for: %s',
                         channel_name)
            return self.get_current_playing_picon_url(
                ''.join(channel_name.split()),
                currservice_serviceref)

        _LOGGER.info('Could not find picon for: %s', channel_name)
        return None

    def load_services(self, bouquet_name=None):
        """
        Load a list of available services, optionally for the supplied bouquet
        :param bouquet_name: name of the bouquet to use when locating services
        :return: list of services discovered
        """

        services = self._load_bouquets(bouquet_name)
        return services

    def _url_exists(self, url):
        """
        Check if a given URL responds to a HEAD request
        :param url: url to test
        :return: True or False
        """
        request = requests.head(url)
        if request.status_code == 200:
            self.cached_urls_which_exist.append(url)
            _LOGGER.debug('cached_urls_which_exist: %s',
                          str(self.cached_urls_which_exist))
            return True

        return False

    @staticmethod
    def get_picon_name(channel_name):
        """
        Get the name as format is outlined here
        https://github.com/OpenViX/enigma2/blob/cc963cd25d7e1c58701f55aa4b382e525031966e/lib/python/Components/Renderer/Picon.py

        :param channel_name: The name of the channel
        :return: the correctly formatted name
        """
        _LOGGER.debug("Getting Picon URL for : " + channel_name)

        channel_name = unicodedata.normalize('NFKD', channel_name) \
            .encode('ASCII', 'ignore')
        channel_name = channel_name.decode("utf-8")
        exclude_chars = ['/', '\\', '\'', '"', '`', '?', ' ', '(', ')', ':',
                         '<', '>', '|', '.', '\n']
        channel_name = re.sub('[%s]' % ''.join(exclude_chars), '',
                              channel_name)
        channel_name = channel_name.replace('&', 'and')
        channel_name = channel_name.replace('+', 'plus')
        channel_name = channel_name.replace('*', 'star')
        channel_name = channel_name.lower()

        return channel_name

    def _invoke_api(self, url, params=None):
        """
        Returns raw response from API
        :param url: URL to call
        :return: Response object
        """

        url = '%s%s' % (self._base, url)
        _LOGGER.debug('About to invoke: %s', url)

        if self._username is not None and self._password is not None:
            self._session.auth = (self._username, self._password)

        if self._use_gzip:
            self._session.headers.update({'Accept-Encoding': 'gzip'})

        # Try to invoke the URL
        try:
            response = self._session.get(url, verify=self._verify_ssl, timeout=self._timeout, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            if response.status_code == 401:
                raise Enigma2Error('Authentication failure - check username and password')
            elif response.status_code == 404:
                raise Enigma2Error(('URL not found %', url))
            else:
                _LOGGER.error('Enigma2 HTTP Error')
                raise Enigma2Error(message='Enigma2 HTTP Error', original=errh)
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error('Failed to connect to server %', url, errc)
            raise Enigma2Error(message='Failed to connect to server', original=errc)

        return response

    def _check_response_result(self, url, params=None):
        """
        :param response:
        :return: Returns True if command success, else, False
        """

        response = self._invoke_api(url, params=params)
        return response.json()['result']

    def _load_bouquets(self, bouquet_name=None):
        """
        Load the bouquet requested or all services
        :param bouquet_name:
        :return:
        """
        from enigma2.constants import URL_BOUQUETS

        from jsonpath_rw import parse
        _LOGGER.debug("Loading all bouquets...")
        service_names = []
        service_refs = []
        e2services = []
        bouquets_response = self._invoke_api(URL_BOUQUETS)
        bouquets_json = bouquets_response.json()

        # If bouquet name supplied, only get those channels
        if bouquet_name in [match.value
                            for match in parse('services[*].servicename').find(bouquets_json)]:
            e2sub_services = [match.value
                              for match in parse('services[*]').find(bouquets_json)]
            for e2sub_service in e2sub_services:
                if e2sub_service['servicename'] == bouquet_name:
                    e2services = e2sub_service['subservices']

        else:
            e2services = [match.value for match in parse('services[*].subservices[*]').find(bouquets_json)]

        for e2service in e2services:
            service_ref = e2service['servicereference']
            service_name = e2service['servicename']

            # only add channel if we've not see it before
            # and it's name/ref pass some basic checks to remove rubbish channels
            if service_ref not in service_refs \
                    and service_ref.endswith(':') \
                    and service_name not in ['<n/a>', '(...)']:
                service_refs.append(service_ref)
                service_names.append(service_name)

        return dict(zip(service_refs, service_names))
