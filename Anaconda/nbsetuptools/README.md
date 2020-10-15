# NOTE

The functionality provided here was superseded by upstream jupyter.
This repo is not in active development.
Thanks!

# NBSetupTools

> Help you install your nbextensions

## Features

* Install nbextensions
* Activate nbextensions
* Activate nbserverextensions
* Disable any extension

## How to use

Install `NBSetupTools` with: `conda install nbsetuptools -c anaconda-nb-extensions` and setup this
boilerplate:

```
extension/
  - extension/
    - nbextension/
      __init__.py
      handlers.py
    - static/
      main.js
      edit.js
      tree.js
    __init__.py
    _version.py
    setup.py         # We will work here!
  setup.py           # Your python setup.py, nothing new here!
  README.mdi         # You need documentation
```

You'll have 2 different `setup.py` files. One is for your `nbserverextension` which
is the same as a python module. There is plenty of documentation about that
[here](https://docs.python.org/2/distutils/index.html).

The next one works with `nbsetuptools` and it should look like:

``` python
from nbsetuptools import setup, find_static

setup(
    name='extension',
    version='0.1.0',
    static=find_static()
)
```

Once you have your module installed you can run:

```
cd extension
python setup.py install --prefix $CONDA_ENV_PATH --enable
python setup.py remove --prefix $CONDA_ENV_PATH
```

## Options available

```
$ python setup.py install --help
usage: setup.py install [-h] [-e] [--path [PATH]] [--overwrite] [--symlink]
                        [--user] [--prefix [PREFIX]]
                        [--nbextensions_dir [NBEXTENSIONS_DIR]]
                        [--destination [DESTINATION]] [--verbose [VERBOSE]]

Install nbextension

optional arguments:
  -h, --help            show this help message and exit
  -e, --enable          Automatically load server and nbextension on notebook
                        launch
  --path [PATH]
  --overwrite
  --symlink
  --user
  --prefix [PREFIX]
  --nbextensions_dir [NBEXTENSIONS_DIR]
  --destination [DESTINATION]
  --verbose [VERBOSE]
```
