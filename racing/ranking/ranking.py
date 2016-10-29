from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import _Logic


class Ranking(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic

    def __init__(self):
        GameObjectMdt.__init__(self)
