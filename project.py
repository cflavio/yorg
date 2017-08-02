# BUGS =====


# TODO LIST =====

# 0.7
# more power for the drifting; the length of the inertia+engine should not
#  be bigger than the max engine's force
# apply drifting force during the drifting
# refactoring of racing.car
# profiling

# 0.8
# store last_version; if last_version != current_version then postprocess
#   option file and change the default e.g.
#   if curr_ver != last_ver & car_num == 7: car_num = 8
# #gaming season

# 0.9 (refinements)
# particles (using shaders)
# preload assets (cars on application's start, track on menu selection)
# give loading feedback for physics parts
# 3D audio (from player's car)
# animation when the car is repaired in pitstop
# use txo files in place of png and jpg
# contour detection
# preloading shaders by creating cards, applying shaders and call render_frame

# 0.10 graphics improvements

# 0.11 (local multiplayer)
# split screen

# 0.12 (network)
# #network at end of a multiplayer race wait for other cars
# #network wheels animations
# #network physics (collisions to players' car)
# #network drivers' names on their cars during multiplayer matches
# #network print if the port is closed when creating the server
# #network send game packets using udp in place of tcp
# #network weapons

# 1.0 (polishment)
# change/improve linux installer
# store the commit of the bam generation to regenerate it only if commits are
#   different


# WAITING =====

# (Panda3D 1.10) #shaders shadows
#     https://www.panda3d.org/forums/viewtopic.php?f=8&t=18798
# (Panda3D 1.10) make 'testing' branch


# MAYBE/SOMEDAY =====

# shaders
# #project make scons for yyagl
# #project embed into a wx / pyqt window
# #project port to python 3
# #shaders deferred shading, tone mapping
# #engine hardware instancing
# #engine multi-threading physics loading
# refactoring DIP, mediator
# #backlog #project make uml diagrams with pyreverse into devinfo
# #backlog #project unit tests
# #backlog #shaders particle effects
# #backlog #mmog django webapp for scores
