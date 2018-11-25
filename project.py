# BUGS =====


# TODO LIST =====

# crash linux mt: remove "load-file-type p3assimp" from config.prc
# profiling


# WAITING =====

# (refactoring server) options: reset pwd, logout
# (refactoring server) mainmenu: multiplayer -> local, online
# (refactoring server) online: login, register -> host (room), join
# (Panda3D 1.10) joypad
# (Panda3D 1.10) remove thirdparty libraries (manage them with deploy-ng)
# (Panda3D 1.10) deployng: use logging for logging
# (Panda3D 1.10) port to python 3
# (Panda3D 1.10) fix curr_ver == 'deploy-ng' in engine.logic
# (Panda3D 1.10) issue 22 (floss drivers for amd)
# (fixed is_in_contact) if not is_in_contact: horizontal ai rays, not inclined
#   like the car (issue 23)
# (test multithreaded render pipeline)


# MAYBE/SOMEDAY =====

# particles with transform feedback
# hardware instancing (gl_InstanceID requires 1.40)
# refactor: use only eng.client (remove eng.server and yorg_client)
# refactor: don't share eng with every colleague, instead share only the
#   useful components e.g. PhysComponent has PhysComponent.phys_mgr and
#   PhysComponent.log_mgr
# refactor: remove mediator from colleague
# refactor: where proper (i.e. where observers aren't tied to the observable)
#   replace observer with publisher-subscriber
# refactor: attach/attach_obs, detach/detach_obs - the client attach-es it to
#   the observed, then it attach-es it to the component
# refactor: Facade.__init__(self, mth_lst, prop_lst), internally it invokes
#   the methods _fwd_mth, _fwd_prop
# refactor: notify's sender (see page.py)
# refactor: invoke Page.__init__
# make a submodule for racing - yyarl
# refactor: racing should be another package (i.e. yorg contains yyagl/ and
#   racing/)
# refactor: do_later with a function that returns a class doesn't work
# embed into a wx / pyqt window
# make scons for yyagl
# unit tests
# django webapp for scores
