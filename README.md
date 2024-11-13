# 2024 ProperData Summer Program

This repo hosts the code for 2024 ProperData Summer Program on Privacy, IoT & AI.

This is no longer updated. ProperData staff please use voice-assistant-internal repo for further development.

## Content

- `voice_assistant_lib.py` -- our library that implements voice assistant building blocks.
- `extra_functions.py` -- extra functions that enhances the voice assistant, used in Lab 6.
- `lab*/*.py` -- our reference lab code.

## Setup on RPi (Automated)

**Warning**: This was only for setting up the environment in our summer program. The script does a bunch of intrusive setup that are unlikely appropriate for general users, like enabling SSH and installing our access key.

```
$ sh env_setup.sh
```

## Custom Setup

Most of the code has been tested on Linux and macOS.

```
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Then try our lab code:

```
$ PYTHONPATH=. python lab6/voice_assistant-carla_with_functions.py
```

