# BUGS =====

# TODO LIST =====

# 0.9 (network)
# crash: sheffield
# think of more race conditions (pun intended)

# 0.10
# add friendship
# add car helios
# refactoring of BitMask32: use constant values in place of magic numbers
# gui revamp
#   feedback: ingame gui - weapon bigger, upperleft or uppercenter corner)
# feedback: couch multiplayer
# feedback: add more cameras
# upnp / pyraknet / nat traversal / hole punching (nattraverso, pypunchp2p,
#   pystun, p2pnat)
# rotate the car towards the direction while flying
# car should be parallel to the ground while flying
# lower mass center
# drifting force function of linear and angular velocities
# after a flight, when a wheel hits the ground, set its friction to 0 and
#   restore it in 0.5 seconds linearly


# WAITING =====

# (Panda3D 1.10) python-keyring for xmpp's credentials
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) write snow shader
# (Panda3D 1.10) hw skinning
# (Panda3D 1.10) make both installer and zip file for linux (for itch.io)
# (Panda3D 1.10) deployng: log_filename
# (Panda3D 1.10) deployng: use logging for logging
# python 3: use keyring_jeepney
# hardware instancing (gl_InstanceID requires 1.40)


# MAYBE/SOMEDAY =====

# refactoring: select the driver before the car
# make scons for yyagl
# embed into a wx / pyqt window
# port to python 3
# uml create automatic class diagrams with fields and methods for each class
# do automatic update (assets shared among platforms)
# unit tests
# django webapp for scores
# refactor: don't share eng with every colleague, instead share only the
#   useful components e.g. PhysComponent has PhysComponent.phys_mgr and
#   PhysComponent.log_mgr
# refactor: remove mediator from colleague
