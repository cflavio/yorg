from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import _Logic
from .event import _Event


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic
    event_cls = _Event
