# Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

import logging
import requests
import json
from xml.etree import ElementTree
from openwebif.constants import DEFAULT_PORT

_LOGGING = logging.getLogger(__name__)

class Client(object):
    """
    Client is the class handling the OpenWebIf interactions.
    """

    def __init__(self, host=None, port=DEFAULT_PORT, username=None, password=None):
        _LOGGING.info("Initialising new openwebif client")

        if not host:
            _LOGGING.error('Missing Openwebif host!')
            return False
        self._host = host

        try:
            import requests
        except ImportError:
            logger.exception(
                "Error while importing dependency requests. "
                "Did you maybe not install the requests dependency?")

            return

    def toggle_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        url = 'http://%s/web/powerstate?newstate=0' % self._host
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        if response.status_code != 200:
            _LOGGING.error("There was an error connecting to %s", url)
            _LOGGING.error("status_code %s", response.status_code)
            _LOGGING.error("error %s", response.error)

            return

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

        url = 'http://%s/api/statusinfo' % self._host
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            _LOGGING.error("There was an error connecting to %s", url)
            _LOGGING.error("status_code %s", response.status_code)
            _LOGGING.error("error %s", response.error)

            return

        _LOGGING.info('r.json: %s', response.json())

        in_standby = response.json()['inStandby']
        _LOGGING.info('r.json inStandby: %s', in_standby)

        return in_standby == 'true'

    def get_status_info(self):
        """
        Returns json containing the result of <host>/api/statusinfo
        """

        url = 'http://%s/api/statusinfo' % self._host
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            _LOGGING.error("There was an error connecting to %s", url)
            _LOGGING.error("status_code %s", response.status_code)
            _LOGGING.error("error %s", response.error)

            return

        return response.json()

