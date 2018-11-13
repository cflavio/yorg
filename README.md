yorg
=========

**Yorg** is an *open source* racing game developed by Ya2 using [Panda3D](http://www.panda3d.org) for *Windows*, *OSX* and *Linux*. More informations can be found on [this page](http://www.ya2.it/pages/yorg.html).

It requires *Python 2.x*. It should be cloned recursively since [yyagl submodule](https://github.com/cflavio/yyagl) is used. 

To run it you should create assets:

* `scons images=1 lang=1 tracks=1`

To use **deploy-ng** the switch `deployng` must be specified, as instance:

* `scons deployng=1 linux_64=1`

To create a build the target OS (`windows`, `osx`, `linux_32`, `linux_64`) should be specified, e.g.:

* `scons linux_64=1`

Prerequisites for building:
* Panda3D;
* SConstruct.

A tutorial for installing and building prerequisites can be found [here](http://www.ya2.it/pages/yorg_setup.html).
