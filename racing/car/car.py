from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt, Ai
from .gfx import _Gfx
from .phys import _Phys
from .event import _Event, _PlayerEvent, _NetworkEvent, _AiEvent
from .logic import _Logic, _PlayerLogic
from .audio import _Audio
from .gui import _Gui
from .ai import _Ai


class Car(GameObjectMdt):
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    event_cls = _Event
    logic_cls = _Logic
    ai_cls = Ai

    def __init__(self, path, pos, hpr, cb, race, laps):
        eng.log_mgr.log('init car')
        self.pos = pos
        self.hpr = hpr
        self.path = path
        self.race = race
        self.laps = laps
        #self.fsm = self.fsm_cls(self)

        #def post_gfx():
        #    pmod = self.race.track.gfx.phys_model
        #    self.phys = self.phys_cls(self, path, pmod)
        #    self.gui = self.gui_cls(self)
        #    self.logic = self.logic_cls(self)
        #    self.audio = self.audio_cls(self)
        #    self.ai = self.ai_cls(self)
        #    self.event = self.event_cls(self)
        #    self.logic.start_pos = pos
        #    self.logic.start_pos_hpr = hpr
        #    eng.log_mgr.log('end init car')
        #    cb()
        #self.gfx = self.gfx_cls(self, path, lambda task: post_gfx())
        GameObjectMdt.__init__(self, cb)

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path, self.race.track.gfx.phys_model]),
             (self.build_gui, 'Gui'),
             (self.build_event, '_Event')],
            [(self.build_logic, '_Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')]]

    def build_logic(self):
        GameObjectMdt.build_logic(self)
        self.logic.start_pos = self.pos
        self.logic.start_pos_hpr = self.hpr

    def build_gfx(self, path):
        self.gfx = self.gfx_cls(self, path)

    def build_phys(self, path, pmod):
        self.phys = self.phys_cls(self, path, pmod)


class PlayerCar(Car):
    event_cls = _PlayerEvent
    audio_cls = _Audio
    gui_cls = _Gui
    logic_cls = _PlayerLogic

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path, self.race.track.gfx.phys_model]),
             (self.build_gui, '_Gui'),
             (self.build_event, '_PlayerEvent')],
            [(self.build_logic, '_PlayerLogic')],
            [(self.build_audio, '_Audio')],
            [(self.build_ai, 'Ai')]]


class NetworkCar(Car):
    event_cls = _NetworkEvent

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path, self.race.track.gfx.phys_model]),
             (self.build_gui, 'Gui'),
             (self.build_event, '_NetworkEvent')],
            [(self.build_logic, '_Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')]]


class AiCar(Car):
    ai_cls = _Ai
    event_cls = _AiEvent

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path, self.race.track.gfx.phys_model]),
             (self.build_gui, 'Gui'),
             (self.build_event, '_AiEvent')],
            [(self.build_logic, '_Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, '_Ai')]]
