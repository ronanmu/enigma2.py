"""
openwebif.api
~~~~~~~~~~~~~~~~~~~~

Provides methods for interacting with OpenWebIf

Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
Licensed under the MIT license.
"""

import logging
import requests
from xml.etree import ElementTree
from openwebif.error import OpenWebIfError, MissingParamError
from openwebif.constants import DEFAULT_PORT
from requests.exceptions import ConnectionError as ReConnError

logging.basicConfig()
_LOGGING = logging.getLogger(__name__)

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

    _LOGGING.error("status_code %s", response.status_code)
    if response.error:
        _LOGGING.error("error %s", response.error)


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
        _LOGGING.info("Initialising new openwebif client")

        if not host:
            _LOGGING.error('Missing Openwebif host!')
            raise MissingParamError('Connection to OpenWebIf failed.', None)

        self._username = username
        self._password = password

        # Now build base url
        self._base = build_url_base(host, port, is_https)

        try:
            _LOGGING.info("Going to probe device to test connection")
            version = self.get_version()
            _LOGGING.info("Connected OK!")
            _LOGGING.info("OpenWebIf version %s", version)

        except ReConnError as conn_err:
            # _LOGGING.exception("Unable to connect to %s", host)
            raise OpenWebIfError('Connection to OpenWebIf failed.', conn_err)

    def toggle_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        url = '%s/web/powerstate?newstate=0' % self._base
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        try:
            tree = ElementTree.fromstring(response.content)
            result = tree.find('e2instandby').text.strip()
            _LOGGING.info('e2instandby: %s', result)

            return result == 'true'

        except AttributeError as attib_err:
            _LOGGING.error(
                'There was a problem toggling standby: %s', attib_err)
            _LOGGING.error('Entire response: %s', response.content)
            return
        return

    def is_box_in_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        in_standby = self.get_status_info()['inStandby']
        _LOGGING.info('r.json inStandby: %s', in_standby)

        return in_standby == 'true'

    def get_about(self, element_to_query=None, timeout=None):
        """
        Returns ElementTree containing the result of <host>/web/about
        or if element_to_query is not None, the value of that element
        """

        url = '%s/web/about' % self._base
        _LOGGING.info('url: %s', url)

        if timeout is not None:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

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
                    _LOGGING.info('element_to_query: %s result: %s',
                                  element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    _LOGGING.error(
                        'There was a problem finding element: %s',
                        element_to_query)

            except AttributeError as attib_err:
                _LOGGING.error(
                    'There was a problem finding element:'
                    ' %s AttributeError: %s', element_to_query, attib_err)
                _LOGGING.error('Entire response: %s', response.content)
                return
        return

    def get_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """

        url = '%s/api/statusinfo' % self._base
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            log_response_errors(response)
            raise OpenWebIfError('Connection to OpenWebIf failed.')

        return response.json()

    def get_version(self):
        """
        Returns Openwebif version
        """
        return self.get_about(
            element_to_query='e2webifversion', timeout=5)
