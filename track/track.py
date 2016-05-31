''''In this module we define the track class.'''
from abc import ABCMeta
from ya2.gameobject import GameObjectMdt
from gfx import _Gfx
from phys import _Phys
from gui import _Gui
from event import _Event
from audio import _Audio
from fsm import _Fsm


class Track(GameObjectMdt):
    '''The Track class.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    gui_cls = _Gui
    event_cls = _Event
    audio_cls = _Audio
    fsm_cls = _Fsm

    def __init__(self, track_path):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self, track_path)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
