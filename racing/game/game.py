from abc import ABCMeta
from .gameobject.gameobject import Logic, GameObjectMdt
from .engine.engine import Engine
import __builtin__


class GameLogic(Logic):

    def on_start(self):
        pass

    def on_end(self):
        pass


class Game(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self, conf):
        __builtin__.game = self
        eng = Engine(conf)
        GameObjectMdt.__init__(self)
        eng.event.register_close_cb(self.logic.on_end)
        self.logic.on_start()
        eng.base.run()
