# Introduction [![Build Status](https://travis-ci.org/ronanmu/enimga2.py.svg?branch=master)](https://travis-ci.org/ronanmu/engima2.py) [![Coverage Status](https://coveralls.io/repos/ronanmu/engima2.py/badge.svg)](https://coveralls.io/r/ronanmu/engima2.py)
enigma2.py is a python module providing a basic python
interface to interact with an Engima2 enabled satellite set-top-box running OpenWebIF

enigma2.py is licensed under the MIT license.

Getting started
===============

enigma2.py is compatible with OWIF 0.4 or newer.
It may work on older versions, but that has not been tested.

For further info on OpenWebIf and it's API's see:
https://github.com/E2OpenPlugins/e2openplugin-OpenWebif

	See file:
	/plugin/controllers/web.py


Requirements
------------

enigma2.py requires:
 * requests>=2.0


Install
-------
```python
pip install enigma2.py
```

# Usage

```python
import enigma2.api

# This will use http by default (not https)
e2_client = enigma2.api.CreateDevice('192.168.2.5')

is_now_in_standby = e2_client.is_box_in_standby()
is_now_in_standby = e2_client.toggle_standby()
xml_response = e2_client.get_about()
json_response = e2_client.get_status_info()
```


TODO
------------
 * https or OpenWebIf authentication is not yet supported.
 * Add get_picon function

Developer
=========

enigma2.py is hosted by Github at https://github.com/ronanmu/enigma2.py.

Code has been tested with the following before commit:

```python
flake8 enigma2
pylint enigma2
coverage run -m unittest discover tests
```

Copyright (c) 2017 Ronan Murray.
