from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import _Logic
from .gui import _Gui


class Ranking(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic
    gui_cls = _Gui
