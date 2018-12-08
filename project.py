# BUGS =====


# TODO LIST =====

# profiling
# particles' recycling
# parameter for emitter's duration
# revert is_in_contact workarounds
# if not is_in_contact: horizontal ai rays, not inclined like the car


# WAITING =====

# (refactoring server) options: reset pwd, logout
# (refactoring server) mainmenu: multiplayer -> local, online
# (refactoring server) online: login, register -> host (room), join
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) deployng: use logging for logging
# (Panda3D 1.10) port to python 3
# (Panda3D 1.10) fix curr_ver == 'deploy-ng' in engine.logic
# (Panda3D 1.10) flatten the track on the target machine (don't build track_all
#   on vps)
# (refactored objects' creation) refactor: facade, pass a single list (meth for
#   for callables, prop for others)


# MAYBE/SOMEDAY =====

# refactor: remove eng.server
# refactor: where proper (i.e. where observers aren't tied to the observable)
#   replace observer with publisher-subscriber
# refactor: attach/attach_obs, detach/detach_obs - the client attach-es it to
#   the observed, then it attach-es it to the component
# refactor: notify's sender (see page.py)
# refactor: object's creation: isolate the parallel creation and construct
#   object in the standard way (fields) and use the parallel creation only when
#   it is useful
# refactor: racing should be another package in another submodule (i.e. yorg
#   contains yyagl/ and racing/)
# make scons for yyagl
# unit tests
