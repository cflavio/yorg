from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .gfx import _Gfx
from .phys import _Phys
from .gui.gui import _Gui
from .event import _Event
from .audio import _Audio
from .fsm import _Fsm


class Track(GameObjectMdt):
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    gui_cls = _Gui
    event_cls = _Event
    audio_cls = _Audio
    fsm_cls = _Fsm

    def __init__(self, track_path, cb, split_world, submodels):
        eng.log_mgr.log('init track')
        self.track_path = track_path
        self.split_world = split_world
        self.submodels = submodels
        #self.fsm = self.fsm_cls(self)

        #def post_gfx():
        #    self.phys = self.phys_cls(self)
        #    self.gui = self.gui_cls(self, track_path[6:])
        #    self.logic = self.logic_cls(self)
        #    self.audio = self.audio_cls(self)
        #    self.ai = self.ai_cls(self)
        #    self.event = self.event_cls(self)
        #    taskMgr.doMethodLater(.01, lambda task: cb(), 'callback')
        #    eng.log_mgr.log('end init track')
        #self.gfx = self.gfx_cls(self, track_path, post_gfx, split_world,
        #                        submodels)
        self.gfx = None
        self.gui = None
        GameObjectMdt.__init__(self, cb)

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, '_Fsm')],
            [(self.build_gfx, '_Gfx', [
                self.track_path, self.split_world, self.submodels]),
             (self.build_phys, '_Phys'),
             (self.build_gui, '_Gui', [self.track_path[6:]])],
            [(self.build_logic, 'Logic')],
            [(self.build_audio, '_Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, '_Event')]]

    def build_gfx(self, track_path, split_world, submodels):
        self.gfx = self.gfx_cls(self, track_path, split_world, submodels)

    def build_gui(self, track_path):
        self.gui = self.gui_cls(self, track_path)
