"""
openwebif.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with OpenWebIf

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
import re, unicodedata
import requests
from xml.etree import ElementTree
from openwebif.error import OpenWebIfError, MissingParamError
from openwebif.constants import DEFAULT_PORT
from requests.exceptions import ConnectionError as ReConnError

log = logging.getLogger(__name__)

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

    log.error("status_code %s", response.status_code)
    if response.error:
        log.error("error %s", response.error)


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
        log.info("Initialising new openwebif client")

        if not host:
            log.error('Missing Openwebif host!')
            raise MissingParamError('Connection to OpenWebIf failed.', None)

        self._username = username
        self._password = password

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        try:
            log.info("Going to probe device to test connection")
            version = self.get_version()
            log.info("Connected OK!")
            log.info("OpenWebIf version %s", version)

        except ReConnError as conn_err:
            raise OpenWebIfError('Connection to OpenWebIf failed.', conn_err)

    def toggle_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        url = '%s/web/powerstate?newstate=0' % self._base
        log.info('url: %s', url)

        response = requests.get(url)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        try:
            tree = ElementTree.fromstring(response.content)
            result = tree.find('e2instandby').text.strip()
            log.info('e2instandby: %s', result)

            return result == 'true'

        except AttributeError as attib_err:
            log.error(
                'There was a problem toggling standby: %s', attib_err)
            log.error('Entire response: %s', response.content)
            return
        return

    def is_box_in_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        in_standby = self.get_status_info()['inStandby']
        log.info('r.json inStandby: %s', in_standby)

        return in_standby == 'true'

    def get_about(self, element_to_query=None, timeout=None):
        """
        Returns ElementTree containing the result of <host>/web/about
        or if element_to_query is not None, the value of that element
        """

        url = '%s/web/about' % self._base
        log.info('url: %s', url)

        if timeout is not None:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)

        log.info('response: %s', response)
        log.info("status_code %s", response.status_code)

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
                    log.info('element_to_query: %s result: %s',
                             element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    log.error(
                        'There was a problem finding element: %s',
                        element_to_query)

            except AttributeError as attib_err:
                log.error(
                    'There was a problem finding element:'
                    ' %s AttributeError: %s', element_to_query, attib_err)
                log.error('Entire response: %s', response.content)
                return
        return

    def get_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """

        url = '%s/api/statusinfo' % self._base
        log.info('url: %s', url)

        response = requests.get(url)

        log.info('response: %s', response)
        log.info("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        return response.json()

    def get_current_playing_picon_url(self):
        """
        Return the URL to the picon image for the currently playing channel
        :return: The URL, or None if not available
        """

        channel_name = self.get_status_info()['currservice_station']
        picon_name = self.get_picon_name(channel_name)

        url = '%s/picon/%s.png' % (self._base, picon_name)
        log.info('picon url: %s', url)
        return url

    def get_picon_name(self, channel_name):
        """
        Get the name as format is outlined here
        https://github.com/OpenViX/enigma2/blob/cc963cd25d7e1c58701f55aa4b382e525031966e/lib/python/Components/Renderer/Picon.py

        :param channel_name: The name of the channel
        :return: the correctly formatted name
        """
        log.info("Getting Picon URL for : " + channel_name)

        exclude_chars = ['/', '\\', '\'', '"', '`', '?', ' ', '(', ')', ':', '<', '>', '|', '.', '\n']
        channel_name = re.sub('[%s]' % ''.join(exclude_chars), '', channel_name)
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
