# Copyright (c) 2015 Finbarr Brady <https://github.com/fbradyirl>
# Licensed under the MIT license.

import logging
import requests
import json
from xml.etree import ElementTree
from openwebif.constants import DEFAULT_PORT
from requests.exceptions import ConnectionError

logging.basicConfig()
_LOGGING = logging.getLogger(__name__)

class Client(object):

    """
    Client is the class handling the OpenWebIf interactions.
    """

    def __init__(self, host=None, port=DEFAULT_PORT,
                 username=None, password=None, https=False):
        _LOGGING.info("Initialising new openwebif client")

        if not host:
            _LOGGING.er.ror('Missing Openwebif host!')
            return None

        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._https = https

        # Now build base url
        self.build_url_base()

        try:
            import requests
        except ImportError:
            _LOGGING.exception(
                "Error while importing dependency requests. "
                "Did you maybe not install the requests dependency?")
            return

        try:
            _LOGGING.info("Going to probe device to test connection")
            version = self.get_about(element_to_query='e2webifversion',timeout=5)
            _LOGGING.info("Connected OK!")
            _LOGGING.info("OpenWebIf version %s", version)

        except ConnectionError as conn_err:
            _LOGGING.exception("Unable to connect to %s", self._host)
            return None


    def build_url_base(self):
        """
        Make base of url based on config
        """
        base = "http"
        if self._https:
            base += 's'

        base += "://"
        base += self._host
        base += ":" 
        base += str(self._port)

        self._base = base

    def log_response_errors(self, response):
        """
        Logs problems in a response
        """

        _LOGGING.error("There was an error connecting to %s", url)
        _LOGGING.error("status_code %s", response.status_code)
        if response.error:
            _LOGGING.error("error %s", response.error)

    def toggle_standby(self):
        """
        Returns True if box is now in standby, else, False
        """

        url = '%s/web/powerstate?newstate=0' % self._base
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        if response.status_code != 200:
            self.log_response_errors(response, url)
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

        url = '%s/api/statusinfo' % self._base
        _LOGGING.info('url: %s', url)

        response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            self.log_response_errors(response, url)
            return

        _LOGGING.info('r.json: %s', response.json())

        in_standby = response.json()['inStandby']
        _LOGGING.info('r.json inStandby: %s', in_standby)

        return in_standby == 'true'


    def get_about(self, element_to_query=None, timeout=None):
        """
        Returns ElementTree containing the result of <host>/web/about
        or if element_to_query is not None, the value of that element
        """

        url = '%s/web/about' % self._base
        _LOGGING.info('url: %s', url)

        if timeout != None:
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.get(url)

        _LOGGING.info('response: %s', response)
        _LOGGING.info("status_code %s", response.status_code)

        if response.status_code != 200:
            self.log_response_errors(response, url)
            return None

        
        if element_to_query == None:
            return response.content
        else:     
            try:
                tree = ElementTree.fromstring(response.content)
                result = tree.findall(".//" + element_to_query)

                if len(result) > 0:
                    _LOGGING.info('element_to_query: %s result: %s', element_to_query, result[0])

                    return result[0].text.strip()
                else:
                    _LOGGING.error(
                        'There was a problem finding element: %s', element_to_query)

            except AttributeError as attib_err:
                _LOGGING.error(
                    'There was a problem finding element: %s AttributeError: %s', element_to_query, attib_err)
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
            self.log_response_errors(response, url)
            return

        return response.json()
