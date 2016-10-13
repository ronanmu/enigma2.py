"""
openwebif.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with OpenWebIf

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
import re
import unicodedata
from xml.etree import ElementTree

import requests
from requests.exceptions import ConnectionError as ReConnError

from openwebif.error import OpenWebIfError, MissingParamError
from openwebif.constants import DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

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


class CreateDevice(object):
    """
    Create a new OpenWebIf client device.
    """

    def __init__(self, host=None, port=DEFAULT_PORT,
                 username=None, password=None, is_https=False):
        enable_logging()
        _LOGGER.info("Initialising new openwebif client")

        if not host:
            _LOGGER.error('Missing Openwebif host!')
            raise MissingParamError('Connection to OpenWebIf failed.', None)

        self._username = username
        self._password = password

        # Used to build a list of URLs which have been tested to exist
        # (for picons)
        self.cached_urls_which_exist = []

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        self._lcd_for_linux_png = '%s/lcd4linux/dpf.png' % self._base

        try:
            _LOGGER.info("Going to probe device to test connection")
            version = self.get_version()
            _LOGGER.info("Connected OK!")
            _LOGGER.info("OpenWebIf version %s", version)

        except ReConnError as conn_err:
            raise OpenWebIfError('Connection to OpenWebIf failed.', conn_err)

    def toggle_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        url = '%s/web/powerstate?newstate=0' % self._base
        _LOGGER.info('url: %s', url)

        response = requests.get(url)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        try:
            tree = ElementTree.fromstring(response.content)
            result = tree.find('e2instandby').text.strip()
            _LOGGER.info('e2instandby: %s', result)

            return result == 'true'

        except AttributeError as attib_err:
            _LOGGER.error(
                'There was a problem toggling standby: %s', attib_err)
            _LOGGER.error('Entire response: %s', response.content)
            return
        return

    def is_box_in_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        in_standby = self.get_status_info()['inStandby']
        _LOGGER.info('r.json inStandby: %s', in_standby)

        return in_standby == 'true'

    def get_about(self, element_to_query=None, timeout=None):
        """
        Returns ElementTree containing the result of <host>/web/about
        or if element_to_query is not None, the value of that element
        """

        url = '%s/web/about' % self._base
        _LOGGER.info('url: %s', url)

        if timeout is not None:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)

        _LOGGER.info('response: %s', response)
        _LOGGER.info("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        if element_to_query is None:
            return response.content
        else:
            try:
                tree = ElementTree.fromstring(response.content)
                result = tree.findall(".//" + element_to_query)

                if len(result) > 0:
                    _LOGGER.info('element_to_query: %s result: %s',
                                 element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    _LOGGER.error(
                        'There was a problem finding element: %s',
                        element_to_query)

            except AttributeError as attib_err:
                _LOGGER.error(
                    'There was a problem finding element:'
                    ' %s AttributeError: %s', element_to_query, attib_err)
                _LOGGER.error('Entire response: %s', response.content)
                return
        return

    def get_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """

        url = '%s/api/statusinfo' % self._base
        _LOGGER.info('url: %s', url)

        response = requests.get(url)

        _LOGGER.info('response: %s', response)
        _LOGGER.info("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        return response.json()

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
            channel_name = self.get_status_info()['currservice_station']

        if currservice_serviceref is None:
            if cached_info is None:
                cached_info = self.get_status_info()
            currservice_serviceref = cached_info['currservice_serviceref']

        if currservice_serviceref.startswith('1:0:0'):
            # This is a recording, not a live channel

            # Todo: parse channel name from currservice_serviceref
            # and get picon based on that

            # As a fallback, send LCD4Linux image (if available)
            url = self._lcd_for_linux_png
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
        _LOGGER.info("Getting Picon URL for : " + channel_name)

        channel_name = unicodedata.normalize('NFKD', channel_name)\
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

    def get_version(self):
        """
        Returns Openwebif version
        """
        return self.get_about(
            element_to_query='e2webifversion', timeout=5)
