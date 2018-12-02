# BUGS =====


# TODO LIST =====

# profiling
# particles with moving emitter


# WAITING =====

# (refactoring server) options: reset pwd, logout
# (refactoring server) mainmenu: multiplayer -> local, online
# (refactoring server) online: login, register -> host (room), join
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) deployng: use logging for logging
# (Panda3D 1.10) port to python 3
# (Panda3D 1.10) fix curr_ver == 'deploy-ng' in engine.logic
# (fixed is_in_contact) if not is_in_contact: horizontal ai rays, not inclined
#   like the car (issue 23)


# MAYBE/SOMEDAY =====

# refactor: remove eng.server
# refactor: where proper (i.e. where observers aren't tied to the observable)
#   replace observer with publisher-subscriber
# refactor: attach/attach_obs, detach/detach_obs - the client attach-es it to
#   the observed, then it attach-es it to the component
# refactor: Facade.__init__(self, mth_lst, prop_lst), internally it invokes
#   the methods _fwd_mth, _fwd_prop
# refactor: notify's sender (see page.py)
# refactor: racing should be another package in another submodule (i.e. yorg
#   contains yyagl/ and racing/)
# make scons for yyagl
# unit tests
