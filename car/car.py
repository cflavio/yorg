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

    def __init__(self, pos, hpr):
        GameObjectMdt.__init__(self)
        self.gfx.nodepath.set_pos(pos)
        self.gfx.nodepath.set_hpr(hpr)
