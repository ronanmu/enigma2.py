# Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

import logging
import requests
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
