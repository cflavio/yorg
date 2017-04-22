yorg
=========

**Yorg** is a free open source racing game developed by Ya2 using Panda3D for Windows, OSX and Linux. More info on [its page](http://www.ya2.it/yorg).

It requires Python 2.x. You should clone it recursively since it uses [yyagl submodule](https://github.com/cflavio/yyagl). In order to run it you should create assets:

* scons images=1 lang=1 tracks=1

If you want to use deploy-ng you must specify the switch ng, as instance:

* scons ng=1 linux_64=1

[![Bountysource Raised](https://www.bountysource.com/badge/team?team_id=213581&style=raised)](https://salt.bountysource.com/teams/ya2)