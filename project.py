# BUGS =====


# TODO LIST =====

# profiling
# restore old tracks' flattening
# joypad
# the server version from a rpc call (not from the file)
# mainmenu: multiplayer -> local, online
# online: login/logout,  register, reset pwd -> host (room), join


# WAITING =====

# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) use logging for logging
# (Panda3D 1.10) port to python 3
# (Panda3D 1.10) fix curr_ver == 'deploy-ng' in engine.logic
# (refactored objects' creation) refactor: facade, pass a single list (meth for
#   for callables, prop for others)
# logging: replace server.start's conn_cb with a message when verbose


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
# rewrite the server using twisted
# make scons for yyagl
