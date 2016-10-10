'''In this module we define the Car classes.'''
from abc import ABCMeta
from gfx import _Gfx
from phys import _Phys
from event import _Event, _PlayerEvent, _NetworkEvent
from logic import _Logic, _PlayerLogic
from audio import _Audio
from gui import _Gui
from ai import _Ai
from racing.game.gameobject.gameobject import GameObjectMdt


class Car(GameObjectMdt):
    '''The Car class models a car.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    event_cls = _Event
    logic_cls = _Logic

    def __init__(self, path, pos, hpr, cb, ai=False):
        eng.log_mgr.log('init car')
        self.fsm = self.fsm_cls(self)
        def post_gfx(task):
            self.phys = self.phys_cls(self, path)
            self.gui = self.gui_cls(self)
            self.logic = self.logic_cls(self)
            self.audio = self.audio_cls(self)
            if ai:
                self.ai_cls = _Ai
            self.ai = self.ai_cls(self)
            self.event = self.event_cls(self)
            self.logic.start_pos = pos
            self.logic.start_pos_hpr = hpr
            eng.log_mgr.log('end init car')
            cb()
        self.gfx = self.gfx_cls(self, path, post_gfx)


class PlayerCar(Car):

    event_cls = _PlayerEvent
    audio_cls = _Audio
    gui_cls = _Gui
    logic_cls = _PlayerLogic


class NetworkCar(Car):

    event_cls = _NetworkEvent
