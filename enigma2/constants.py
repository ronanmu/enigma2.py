"""
enigma2.constants
~~~~~~~~~~~~~~~~~~~~

List of constants

Copyright (c) 2018 Ronan Murray <https://github.com/ronanmu>
Licensed under the MIT license.
"""

DEFAULT_PORT = 80

PARAM_SEARCH = "search"
PARAM_NEWSTATE = "newstate"
PARAM_COMMAND = "command"

COMMAND_RC_CHANNEL_UP = "402"
COMMAND_RC_CHANNEL_DOWN = "403"
COMMAND_RC_PLAY_PAUSE_TOGGLE = "207"

COMMAND_VOL_MUTE = "mute"
COMMAND_VOL_UP = "up"
COMMAND_VOL_SET = "set"
COMMAND_VOL_DOWN = "down"

URL_VOLUME = "/api/vol"
URL_ABOUT = "/api/about"
URL_TOGGLE_STANDBY = "/api/powerstate"
URL_STATUS_INFO = "/api/statusinfo"
URL_BOUQUETS = "/api/getallservices"
URL_EPG_SEARCH = "/api/epgsearch"
URL_REMOTE_CONTROL = "/api/remotecontrol"
URL_LCD_4_LINUX = "/lcd4linux/dpf.png"
