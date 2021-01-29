yorg
=========

**Yorg** is an *open source* racing game developed by Ya2 using [Panda3D](http://www.panda3d.org) for *Windows*, *OSX* and *Linux*. More information can be found on [this page](http://www.ya2.it/pages/yorg.html).

It requires *Python 3.x*. It should be cloned recursively since [yyagl submodule](https://github.com/cflavio/yyagl) and [yracing submodule](https://github.com/cflavio/yracing) are used.

To run it you should create assets:

* `python setup.py images lang models`

To create the builds, you can use the awesome Panda3D's deployment tools:

* `python setup.py bdist_apps`

Here's a short guide about installing and preparing your environment for Yorg.

* clone the repository: `git clone --recursive https://github.com/cflavio/yorg.git`
* go into the directory: `cd yorg`
* (optional, recommended for non-developers, since *master* is an unstable branch) checkout the *stable* branch: `git checkout stable; git submodule foreach git checkout stable`
* create a python3 virtualenv: `virtualenv --python=/usr/bin/python3 venv`
* activate the virtualenv: `. ./venv/bin/activate`
* install the prerequisites: `pip install -r requirements.txt`
* build the required assets: `python setup.py lang images models`
* launch the game: `python main.py`

Here's a screenshot:

![Yorg](assets/images/yorg.jpg)
