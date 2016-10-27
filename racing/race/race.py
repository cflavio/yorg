from abc import ABCMeta
from racing.game.gameobject.gameobject import GameObjectMdt
from .logic import _Logic


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic

    def __init__(self, track):
        GameObjectMdt.__init__(self)
        self.track = track
