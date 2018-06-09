# BUGS =====

# TODO LIST =====

# 0.10 (local multiplayer)
# add car helios
# gui revamp
#   feedback: ingame gui - weapon bigger, upperleft or uppercenter corner)
#   speed: speed number with a semicircle with a shader
# feedback: couch multiplayer
# lower mass center
# after a flight, when a wheel hits the ground, set its friction to 0 and
#   restore it in 0.5 seconds linearly

# 0.11 (better online multiplayer)
# do a single page with track, drivers, cars and messages for all: single,
#  local and online multiplayer
# refactoring: select the driver before the car
# make a client-server solution (server on ya2tech.it) (advantages: doesn't
#   require port forwarding, robust - no match server)
# refactoring of yorg server and players' servers: use rpc
# upnp / pyraknet / nat traversal / hole punching (nattraverso, pypunchp2p,
#   pystun, p2pnat)
# evaluate stun server - pystun or some stun lib
# evaluate reliable udp: enet, raknet, ...

# 0.12 (more cameras)
# add friendship
# feedback: add more cameras
# drifting force function of linear and angular velocities


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
# (rpyc) refactoring of protocol: use less xmpp and more rpyc (easier
#  concurrency management), also for the server
# (rpyc) refactoring network: use bjson for exchanging data
# (rpyc) remove xmpp: register users from the game with a db on the server,
#   player's disconnection using socket () - evaluate, I'm not sure


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
# refactor: remove mediator from colleague
