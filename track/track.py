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
