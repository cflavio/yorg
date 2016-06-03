'''In this module we define the Car classes.'''
from abc import ABCMeta
from gfx import _Gfx
from phys import _Phys
from event import _Event
from logic import _Logic
from audio import _Audio
from gui import _Gui
from ya2.gameobject import GameObjectMdt

class Car(GameObjectMdt):
    '''The Car class models a car.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    event_cls = _Event
    logic_cls = _Logic
    audio_cls = _Audio
    gui_cls = _Gui

    def __init__(self, path, pos, hpr):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self, path)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
        self.logic.start_pos = pos
        self.logic.start_pos_hpr = hpr
