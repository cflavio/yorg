# BUGS =====


# TODO LIST =====

# port the server to python 3
# installers (remove linux32 build)
# use logging for logging
# joypad
# fix curr_ver == 'deploy-ng' in engine.logic
# make a builder which uses pre-built assets, if it works
#   on vps then make a trigger for git updates and manage the output (create a
#   webpage which contains builds and logs)
# fix pause (it doesn't stop the time)
# remove the multiplayer frame


# WAITING =====

# (refactored objects' creation): facade, pass a single list (meth for
#   callables, prop for others)
# logging: replace server.start's conn_cb with a message when verbose


# MAYBE/SOMEDAY =====

# profiling
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
# move all track's assets (minimap, menu image, ...) in track's folder
# gui warnings for missing track's logics information
# retrieve track list from 'tracks' folder (don't use an hardcoded list) (mods)
# retrieve car list from 'cars' folder (don't use an hardcoded list) (mods)
