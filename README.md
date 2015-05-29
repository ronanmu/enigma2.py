Provides a basic python interface to interact with a device running OpenWebIf

# Installation (use sudo if needed)

```python
git clone --recursive https://github.com/fbradyirl/openwebif.py.git
cd openwebif
pip install -r requirements.txt
pip install -e .
```

# Usage

```python
import openwebif.api

e2_client = openwebif.api.Client('192.168.2.5')

is_now_in_standby = e2_client.toggle_standby()
```
