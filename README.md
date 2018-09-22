yorg
=========

**Yorg** is an *open source* racing game developed by Ya2 using [Panda3D](http://www.panda3d.org) for *Windows*, *OSX* and *Linux*. More info on [its page](http://www.ya2.it/pages/yorg.html).

It requires *Python 2.x*. You should clone it recursively since it uses [yyagl submodule](https://github.com/cflavio/yyagl). In order to run it you should create assets:

* `scons images=1 lang=1 tracks=1`

If you want to use **deploy-ng** you must specify the switch `deployng`, as instance:

* `scons deployng=1 linux_64=1`

In order to create a build you should specify the target OS (`windows`, `osx`, `linux_32`, `linux_64`) e.g.:

* `scons linux_64=1`

Prerequisites for building:
* Panda3D;
* SConstruct.

You can find a tutorial for installing and building prerequisites [here](http://www.ya2.it/pages/yorg_setup.html).
