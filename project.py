# BUGS =====

# TODO LIST =====

# 0.10 (better multiplayer)
# add logging

# 0.11 (local multiplayer)
# local multiplayer


# WAITING =====

# (Panda3D 1.10) python-keyring for xmpp's credentials
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) write snow shader
# (Panda3D 1.10) hw skinning
# (Panda3D 1.10) deployng: log_filename
# (Panda3D 1.10) deployng: use logging for logging
# (Panda3D 1.10) port to python 3
# python 3: use keyring_jeepney
# hardware instancing (gl_InstanceID requires 1.40)


# MAYBE/SOMEDAY =====

# make scons for yyagl
# embed into a wx / pyqt window
# uml create automatic class diagrams with fields and methods for each class
# do automatic update (assets shared among platforms)
# unit tests
# django webapp for scores
# refactor: don't share eng with every colleague, instead share only the
#   useful components e.g. PhysComponent has PhysComponent.phys_mgr and
#   PhysComponent.log_mgr
# refactor: remove mediator from colleague
# add car helios
# add friendship
# drifting force function of linear and angular velocities
# do a single page with track, drivers, cars and messages for all: single,
#  local and online multiplayer
# refactoring: select the driver before the car
# make a client-server solution (server on ya2tech.it) (advantages: doesn't
#   require port forwarding, robust - no match server)
# refactoring of protocol: use less xmpp and more rpyc (easier concurrency
#   management), also for the server
# remove xmpp: register users from the game with a db on the server, player's
#   disconnection using socket () - evaluate, I'm not sure
# refactoring (network): use bjson for exchanging data
