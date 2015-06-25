''''In this module we define the track class.'''
from abc import ABCMeta
from ya2.gameobject import GameObjectMdt
from gfx import _Gfx
from phys import _Phys
from gui import _Gui


class Track(GameObjectMdt):
    '''The Track class.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    gui_cls = _Gui
