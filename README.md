# Introduction 
[![Build Status](https://travis-ci.org/ronanmu/enigma2.py.svg?branch=master)](https://travis-ci.org/ronanmu/enigma2.py) [![Coverage Status](https://coveralls.io/repos/ronanmu/enigma2.py/badge.svg)](https://coveralls.io/r/ronanmu/enigma2.py)

enigma2.py is a python module providing a python
interface to interact with an Engima2 enabled satellite set-top-box running OpenWebIF

enigma2.py is licensed under the MIT license.

Getting started
===============

enigma2.py is compatible with OWIF 0.4 or newer.
It may work on older versions, but that has not been tested.

For further info on OpenWebIf and it's API's see:
https://github.com/E2OpenPlugins/e2openplugin-OpenWebif


Details of the full list of functions available in OpenWebIf are listed [here](https://dream.reichholf.net/wiki/Enigma2:WebInterface)

Requirements
------------

enigma2.py requires:
 * requests>=2.0
 * jsonpath-rw


Install
-------
```python
pip install enigma2.py
```

# Usage

```python
import enigma2.api

# Connect to an Enigma2 box at http://123.123.123.123
device = enigma2.api.Enigma2Connection(host='123.123.123.123')

# Power on the device
is_now_in_standby = device.is_box_in_standby()

# Set the volume to 45
request_success = device.set_volume(45)

# Search for Home and Away in the current EPG
epg_results = device.search_epg('Home and Away')

```



Developer
=========

enigma2.py is hosted by Github at https://github.com/ronanmu/enigma2.py.

Code has been tested with the following before commit:

```shell
flake8 enigma2
pylint enigma2
coverage run --source enigma2 -m unittest discover tests
```

Copyright (c) 2018 Ronan Murray.
