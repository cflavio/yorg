# BUGS =====


# TODO LIST =====

# profiling
# restore old tracks' flattening
# mainmenu: multiplayer -> local, online
# online: login/logout,  register, reset pwd -> host (room), join


# WAITING =====

# Panda3D 1.10: remove thirdparty libraries (manage them with deploy-ng); use
#   logging for logging; port to python 3; remove linux32 build;
#   fix curr_ver == 'deploy-ng' in engine.logic; installers
# py3; joypad
# (refactored objects' creation): facade, pass a single list (meth for
#   callables, prop for others)
# logging: replace server.start's conn_cb with a message when verbose


# MAYBE/SOMEDAY =====

# lib/p3d/gui.py, lib/p3d/gfx.py: __init__ method from a non direct base class
#   'Facade' is called
# remove eng.server
# where proper (i.e. where observers aren't tied to the observable) replace
#   observer with publisher-subscriber
# attach/attach_obs, detach/detach_obs - the client attach-es it to the
#   observed, then it attach-es it to the component
# notify's sender (see page.py)
# object's creation: isolate the parallel creation and construct object in the
#   standard way (fields) and use the parallel creation only when it is useful
# racing should be another package in another submodule (i.e. yorg contains
#   yyagl/ and racing/)
# yyagl's scons; use twisted for the server; unit tests; webapp; track editor
