# BUGS =====

# TODO LIST =====

# 0.8
# engine's audio when the user accelerates at start
# engine's audio for gears
# particles (using shaders)
# particles for crashes
# particles for skidmarks/trail
# particles for weapons
# camera at car's back
# preload assets (cars on application's start, track on menu selection)
# animation when the car is repaired in pitstop
# animation when the car is hit by rotate_all
# use txo files in place of png and jpg
# contour detection
# preload weapons
# ai polling (for cars and directions); only one (rotated) ray for obstacles
#   and ground
# try the driving models with lighter cars
# driving model - see https://forum.freegamedev.net/viewtopic.php?p=74451#p74451
# more power for the drifting; the length of the inertia+engine should not
#  be bigger than max engine's force
# apply drifting force during the drifting

# 0.9 (network)
# #network at end of a multiplayer race wait for other cars
# #network wheels' animations
# #network physics (collisions to players' car)
# #network drivers' names on their cars during multiplayer matches
# #network print if the port is closed when creating the server
# #network send game packets using udp in place of tcp
# #network weapons


# WAITING =====

# (Panda3D 1.10) #shaders shadows
#     https://www.panda3d.org/forums/viewtopic.php?f=8&t=18798
# (Panda3D 1.10) make 'testing' branch


# MAYBE/SOMEDAY =====

# preloading shaders by creating cards, applying shaders and call render_frame
# 3D audio (from player's car)
# refactor: notify done by evt (from mdt externally);
#   Colleague.notify invokes that; GO's attach redirected to evt;
#   only evt is a Subject
# remove mdt from colleague
# change/improve linux installer
# make scons for yyagl
# embed into a wx / pyqt window
# port to python 3
# deferred shading, tone mapping
# hardware instancing
# multi-threading physics loading
# make uml diagrams with pyreverse into devinfo
# unit tests
# django webapp for scores
