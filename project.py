# ================================= BUGS ======================================

# build linux: pitstop's animation (only with shaders)
# back from room


# ============================== TODO LIST ====================================


# =============================== WAITING =====================================

# flatpak on the vps: issues #28


# ============================ MAYBE/SOMEDAY ==================================

# profiling
# remove camera's render_all workaround
# portable installers (xz)
# refactor the server (async.io) or
#     def update(): ... threading.Timer(.5, update).start()
# refactoring: do event/observer for joystick buttons
# remove dependencies: bson (struct), pyyaml (configparser+json),
#   feedparser (write my function which retrieve posts' titles)
# use python's logging in place of eng.log
# lib/p3d/gui.py, lib/p3d/gfx.py: __init__ method from a non direct base class
#   'Facade' is called
# remove eng.server
# class Player (has-a car, has-a driver)
# where proper (i.e. where observers aren't tied to the observable) replace
#   observer with publisher-subscriber
# attach/attach_obs, detach/detach_obs - the client attach-es it to the
#   observed, then it attach-es it to the component
# notify's sender (see page.py)
# object's creation: isolate the parallel creation and construct object in the
#   standard way (fields) and use the parallel creation only when it is useful
# (waitig for refactored objects' creation): facade, pass a single list (meth
#   for callables, prop for others)
# racing should be another package in another submodule (i.e. yorg contains
#   yyagl/ and racing/)
# yyagl's scons
# unit tests
# move all track's assets (minimap, menu image, ...) in track's folder
# gui warnings for missing track's logics information
# retrieve track list from 'tracks' folder (don't use an hardcoded list) (mods)
# retrieve car list from 'cars' folder (don't use an hardcoded list) (mods)
# loadPrcFileData('', 'framebuffer-srgb true'); texture.set_format(F_srgb)
# https://discourse.panda3d.org/t/sample-using-directional-lights-shadows-effectively/24424
