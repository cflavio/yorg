from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt, Ai
from .gfx import _Gfx
from .phys import CarPhys
from .event import _Event, _PlayerEvent, _PlayerEventServer, \
    _PlayerEventClient, _NetworkEvent, _AiEvent
from .logic import CarLogic, _PlayerLogic
from .audio import _Audio
from .gui import CarGui
from .ai import _Ai


class Car(GameObjectMdt):
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = CarPhys
    event_cls = _Event
    logic_cls = CarLogic
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
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self, self.path]),
             ('phys', self.phys_cls, [self, self.path,
                                         self.race.track.phys.model]),
             ('gui', self.gui_cls, [self]),
             ('event', self.event_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst, cb)
        self.logic.start_pos = self.pos
        self.logic.start_pos_hpr = self.hpr


class PlayerCar(Car):
    event_cls = _PlayerEvent
    audio_cls = _Audio
    gui_cls = CarGui
    logic_cls = _PlayerLogic


class PlayerCarServer(Car):
    event_cls = _PlayerEventServer
    audio_cls = _Audio
    gui_cls = CarGui
    logic_cls = _PlayerLogic


class PlayerCarClient(Car):
    event_cls = _PlayerEventClient
    audio_cls = _Audio
    gui_cls = CarGui
    logic_cls = _PlayerLogic


class NetworkCar(Car):
    event_cls = _NetworkEvent


class AiCar(Car):
    ai_cls = _Ai
    event_cls = _AiEvent
