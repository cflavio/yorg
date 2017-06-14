# BUGS =====

# fix for the prototype track


# TODO LIST =====

# 0.6
# remove some XProps (there should be only SeasonProps, RaceProps, ...)
# remove on_frame spikes in profiling
# remove Draw/Clear spikes in profiling

# 0.7
# forward missile
# backward missile
# turbo
# drop a fixed bomb
# rotate-all bomb
# #ai weapons
# refactoring of racing.race
# refactoring of racing.track
# refactoring of racing.car
# refactoring of racing

# 0.8
# #gaming season

# 0.9
# #network at end of a multiplayer race wait for other cars
# #network wheels animations
# #network physics (collisions to players' car)
# #network drivers' names on their cars during multiplayer matches
# #network print if the port is closed when creating the server
# #network send game packets using udp in place of tcp
# #network weapons

# 1.0 (refinements)
# preload assets (cars on application's start, track on menu selection)
# give loading feedback for physics parts
# store the commit of the bam generation to regenerate it only if commits are
#   different
# 3D audio (from player's car)
# deployed textures should have power-of-2 dimensions
# ai poller: process one car's ai for each frame
# drifting
# animation when the car is repaired in pitstop


# WAITING =====

# (Panda3D 1.10) #shaders shadows
#     https://www.panda3d.org/forums/viewtopic.php?f=8&t=18798
# (Panda3D 1.10) make 'testing' branch


# MAYBE/SOMEDAY =====

# #project make scons for yyagl
# #project embed into a wx / pyqt window
# #project port to python 3
# #shaders deferred shading, tone mapping; fxaa
# #engine hardware instancing
# #engine multi-threading physics loading
# refactoring DIP, mediator
# refactoring engine -> several singletons (LogMgr, PhysMgr, ...)
# refactoring do only RaceProps, SeasonProps, MenuProps, ... and project them
#   when passing
# #backlog #project make uml diagrams with pyreverse into devinfo
# #backlog #project unit tests
# #backlog #shaders particle effects
# #backlog #mmog django webapp for scores
