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
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError as ReConnError
from enigma2.error import Enigma2Error

_LOGGER = logging.getLogger(__name__)

URL_ABOUT = "/api/about"
URL_TOGGLE_VOLUME_MUTE = "/api/vol?set=mute"
URL_SET_VOLUME = "/api/vol?set=set"
URL_TOGGLE_STANDBY = "/api/powerstate?newstate=0"
URL_STATUS_INFO = "/api/statusinfo"

# Remote control commands
URL_REMOTE_CONTROL = "/api/remotecontrol?command="
COMMAND_VU_CHANNEL_UP = "402"
COMMAND_VU_CHANNEL_DOWN = "403"
COMMAND_VU_PLAY_PAUSE_TOGGLE = "207"

URL_LCD_4_LINUX = "/lcd4linux/dpf.png"


class PlaybackType(Enum):
    """ Enum for Playback Type """
    live = 1
    recording = 2
    none = 3


# pylint: disable=too-many-arguments


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


def log_response_errors(response):
    """
    Logs problems in a response
    """

    _LOGGER.error("status_code %s", response.status_code)
    if response.error:
        _LOGGER.error("error %s", response.error)


def enable_logging():
    """ Setup the logging for home assistant. """
    logging.basicConfig(level=logging.INFO)


class Enigma2Connection(object):
    """
    Create a new Connection to an Enigma.
    """

    def __init__(self, url=None, host=None, port=None,
                 username=None, password=None, is_https=False, timeout=5, verify_ssl=True):
        enable_logging()
        _LOGGER.debug("Initialising new Enigma2 OpenWebIF client")

        if not host and not url:
            _LOGGER.error('Missing Enigma2 host!')
            raise Enigma2Error('Connection to Enigma2 failed - please supply connection details')

        self._username = username
        self._password = password
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._in_standby = True

        # Used to build a list of URLs which have been tested to exist
        # (for picons)
        self.cached_urls_which_exist = []

        # Now build base url
        if not url:
            self._base = build_url_base(host, port, is_https)
        else:
            self._base = url

        try:
            _LOGGER.debug("Going to probe device to test connection")
            self.get_status_info()
            _LOGGER.debug("Connected OK!")

        except ReConnError as conn_err:
            raise Enigma2Error('Connection to Enigma2 failed.', conn_err)

    def set_volume(self, new_volume):
        """
        Sets the volume to the new value

        :param new_volume: int from 0-100
        :return: True if successful, false if there was a problem
        """

        if new_volume < -1 and new_volume > 101:
            raise Enigma2Error('Volume must be between 0 and 100')

        url = '%s%s' % (URL_SET_VOLUME, str(new_volume))
        return self._check_response_result(url)

    def toggle_standby(self):
        """
        Returns True if command success, else, False
        """
        result = self._check_response_result(URL_TOGGLE_STANDBY)
        # Update standby
        self.get_status_info()
        return result

    def xxtoggle_play_pause(self):
        """
        Send Play Pause command
        """

        url = '%s%s%s' % (self._base, URL_REMOTE_CONTROL,
                          COMMAND_VU_PLAY_PAUSE_TOGGLE)
        _LOGGER.info('url: %s', url)

        return self._check_response_result(requests.get(url))

    def channel_up(self):
        """
        Send channel up command
        """

        url = '%s%s' % (URL_REMOTE_CONTROL, COMMAND_VU_CHANNEL_UP)
        return self._check_response_result(url)

    def channel_down(self):
        """
        Send channel down command
        """

        url = '%s%s' % (URL_REMOTE_CONTROL, COMMAND_VU_CHANNEL_DOWN)
        return self._check_response_result(url)

    def mute_volume(self):
        """
        Send mute command
        """
        return self._check_response_result(URL_TOGGLE_VOLUME_MUTE)

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

        response = self._invoke_api(URL_STATUS_INFO)
        response_json = response.json()
        self._in_standby = response_json['inStandby']
        return response_json

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
        cached_info = None
        if channel_name is None:
            cached_info = self.get_status_info()
            if 'currservice_station' in cached_info:
                channel_name = cached_info['currservice_station']
            else:
                _LOGGER.info('No channel currently playing')
                return None

        if currservice_serviceref is None:
            if cached_info is None:
                cached_info = self.get_status_info()
            currservice_serviceref = cached_info['currservice_serviceref']

        if currservice_serviceref.startswith('1:0:0'):
            # This is a recording, not a live channel

            # Todo: parse channel name from currservice_serviceref
            # and get picon based on that

            # As a fallback, send LCD4Linux image (if available)
            url = '%s%s' % (self._base, URL_LCD_4_LINUX)
            _LOGGER.info('This is a recording, trying url: %s', url)

        else:
            picon_name = self.get_picon_name(channel_name)
            url = '%s/picon/%s.png' % (self._base, picon_name)

        if url in self.cached_urls_which_exist:
            _LOGGER.info('picon url (already tested): %s', url)
            return url

        if self.url_exists(url):
            _LOGGER.info('picon url: %s', url)
            return url

        # Last ditch attenpt. If channel ends in HD, lets try
        # and get non HD picon
        if channel_name.lower().endswith('hd'):
            channel_name = channel_name[:-2]
            _LOGGER.info('Going to look for non HD picon for: %s',
                         channel_name)
            return self.get_current_playing_picon_url(
                ''.join(channel_name.split()),
                currservice_serviceref)

        _LOGGER.info('Could not find picon for: %s', channel_name)
        return None

    def url_exists(self, url):
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

    def _invoke_api(self, url):
        """
        Returns raw response from API
        :param url: URL to call
        :return: Response object
        """

        url = '%s%s' % (self._base, url)
        _LOGGER.debug('About to invoke: %s', url)

        if not self._username and not self._password:
            response = requests.get(url, verify=self._verify_ssl, timeout=self._timeout)
        else:
            response = requests.get(url, verify=self._verify_ssl, timeout=self._timeout,
                                    auth=HTTPBasicAuth(self._username, self._password))

        if response.status_code == 401:
            _LOGGER.warning('Engima2 Authentication failure')
            raise Enigma2Error('Authentication failure - check username and password')
        elif response.status_code == 500:
            _LOGGER.error('Engima2 server error')
            log_response_errors(response)
            raise Enigma2Error('Engima2 server error for request' + url)
        elif response.status_code == 200:
            _LOGGER.debug('Response received OK')

        return response

    def _check_response_result(self, url):
        """
        :param response:
        :return: Returns True if command success, else, False
        """

        response = self._invoke_api(url)
        return response.json()['result']
