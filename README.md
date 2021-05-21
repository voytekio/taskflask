# taskflask
## Overview
task app with flask api
## Syntax
* `taskcmd --help`
* `taskcmd -t -f tklr3.1.txt`

## Dev
### New Dev
* new dev should use proper src format(src/<pkg_name>/<any>.py) , -m, probably no need for -e, but may need a virtenv with dependencies installed from requirements, otherwise you'll have to install them everytime
### Old Dev - using -e installable mode
* this requires you have a symlink in your repos/taskflask dir: `ln -s src taskflask`. Symlink likeely invalidates fully testing imports
* create a dev virtualenv: `virtualenv ~/venvs/tklr_dev`, activate it
* pip install dependencies from either setup.py or requirements.txt
* pip install your pkg in Editable mode: `pip install -e ~/repos/taskflask`
* run with `taskcmd --help` (from your repos/taskflask dir)
* use sample test file from `<repo>/tests/assets/[assets.txt or today.txt]` (make a copy first)

## Tests
* activate a venv with tox installed
* cd into repo dir (with tox.ini file)
* list tox tests with `tox -l`
* run with `tox -e <tox_test>` ex: `tox -e unit`
