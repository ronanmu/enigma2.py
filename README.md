# openwebif.py
Provides a python interface to interact with a device running OpenWebIf

To run, point to the Enigma2 host:

import openwebif.api

openweb_api = openwebif.api.Client('192.168.2.5')

# Then try to do an action
is_in_standby = openweb_api.toggle_standby()

