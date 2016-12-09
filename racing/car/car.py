from racing.game.gameobject import GameObjectMdt, Ai
from .gfx import CarGfx
from .phys import CarPhys
from .event import CarEvent, CarPlayerEvent, CarPlayerEventServer, \
    CarPlayerEventClient, CarNetworkEvent, CarAiEvent
from .logic import CarLogic, CarPlayerLogic
from .audio import CarAudio
from .gui import CarGui
from .ai import CarAi


class Car(GameObjectMdt):
    gfx_cls = CarGfx
    phys_cls = CarPhys
    event_cls = CarEvent
    logic_cls = CarLogic
    ai_cls = Ai

    def __init__(self, path, pos, hpr, cb, race, laps):
        eng.log_mgr.log('init car')
        self.pos = pos
        self.hpr = hpr
        self.path = path
        self.race = race
        self.laps = laps
        init_lst = [
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
    event_cls = CarPlayerEvent
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class PlayerCarServer(Car):
    event_cls = CarPlayerEventServer
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class PlayerCarClient(Car):
    event_cls = CarPlayerEventClient
    audio_cls = CarAudio
    gui_cls = CarGui
    logic_cls = CarPlayerLogic


class NetworkCar(Car):
    event_cls = CarNetworkEvent


class AiCar(Car):
    ai_cls = CarAi
    event_cls = CarAiEvent
