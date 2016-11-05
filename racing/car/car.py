from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt, Ai
from .gfx import _Gfx
from .phys import _Phys
from .event import _Event, _PlayerEvent, _PlayerEventServer, \
    _PlayerEventClient, _NetworkEvent, _AiEvent
from .logic import CarLogic, _PlayerLogic
from .audio import _Audio
from .gui import CarGui
from .ai import _Ai


class Car(GameObjectMdt):
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    event_cls = _Event
    logic_cls = CarLogic
    gui_cls = CarGui
    ai_cls = Ai

    def __init__(self, path, pos, hpr, cb, race, laps):
        eng.log_mgr.log('init car')
        self.pos = pos
        self.hpr = hpr
        self.path = path
        self.race = race
        self.laps = laps
        self.gfx = None
        self.gui = None
        GameObjectMdt.__init__(self, self.init_lst, cb)

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_Event')],
            [(self.build_logic, 'CarLogic')],
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
    gui_cls = CarGui
    logic_cls = _PlayerLogic

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_PlayerEvent')],
            [(self.build_logic, '_PlayerLogic')],
            [(self.build_audio, '_Audio')],
            [(self.build_ai, 'Ai')]]


class PlayerCarServer(Car):
    event_cls = _PlayerEventServer
    audio_cls = _Audio
    gui_cls = CarGui
    logic_cls = _PlayerLogic

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_PlayerEventServer')],
            [(self.build_logic, '_PlayerLogic')],
            [(self.build_audio, '_Audio')],
            [(self.build_ai, 'Ai')]]


class PlayerCarClient(Car):
    event_cls = _PlayerEventClient
    audio_cls = _Audio
    gui_cls = CarGui
    logic_cls = _PlayerLogic

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, '_Gfx', [self.path]),
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_PlayerEventClient')],
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
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_NetworkEvent')],
            [(self.build_logic, 'CarLogic')],
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
             (self.build_phys, '_Phys', [self.path,
                                         self.race.track.gfx.phys_model]),
             (self.build_gui, 'CarGui'),
             (self.build_event, '_AiEvent')],
            [(self.build_logic, 'CarLogic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, '_Ai')]]
