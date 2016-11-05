from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .gfx import _Gfx
from .phys import _Phys
from .gui.gui import TrackGui
from .event import _Event


class Track(GameObjectMdt):
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    gui_cls = TrackGui
    event_cls = _Event

    def __init__(self, track_path, cb, split_world, submodels):
        eng.log_mgr.log('init track')
        self.track_path = track_path
        self.gfx = None
        self.gui = None
        init_lst = [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [
                self.track_path, split_world, submodels]),
             (self.build_phys, '_Phys'),
             (self.build_gui, 'TrackGui', [self.track_path[6:]])],
            [(self.build_logic, 'Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, '_Event')]]
        GameObjectMdt.__init__(self, init_lst, cb)

    def build_gfx(self, track_path, split_world, submodels):
        self.gfx = self.gfx_cls(self, track_path, split_world, submodels)

    def build_gui(self, track_path):
        self.gui = self.gui_cls(self, track_path)
