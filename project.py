# BUGS =====


# TODO LIST =====

# 0.9 (network)
# weapons fired (mine)
# manage multiple weapons e.g. drop two mines then collect and fire a rocket
# physics (collisions to players' car)
# physics for weapons
# patroners' badge
# redirect xmpp callbacks in the main thread
# test three players


# 0.10
# add car helios
# more gravity and heavier cars
# feedback: steering feels a bit restricted and overly punishing (i.e. easy to
#   loose control)
# try to reduce adherence as soon as you turn, then restore it
# gui revamp
#   feedback: ingame gui - weapon bigger, upperleft or uppercenter corner)
# feedback: in crossroads is unclear where to turn - add an indication?
# feedback: couch multiplayer
# feedback: add more cameras


# WAITING =====

# (Panda3D 1.10) python-keyring for xmpp's credentials
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# python 3: use keyring_jeepney
# hardware instancing (gl_InstanceID requires 1.40)


# MAYBE/SOMEDAY =====

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
# refactor: remove mdt from colleague
