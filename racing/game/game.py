from abc import ABCMeta
from .gameobject import Logic, GameObjectMdt
from .engine.engine import EngineWindow
import __builtin__
import sys


class GameLogic(Logic):

    def on_start(self):
        pass

    def on_end(self):
        pass


class Game(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self, classes, conf):
        __builtin__.game = self
        eng = EngineWindow(conf)
        init_lst = [
            [('fsm', classes[0], [self])],
            [('gfx', classes[1], [self])],
            [('phys', classes[2], [self])],
            [('gui', classes[3], [self])],
            [('logic', classes[4], [self])],
            [('audio', classes[5], [self])],
            [('ai', classes[6], [self])],
            [('event', classes[7], [self])]]
        GameObjectMdt.__init__(self, init_lst)
        eng.event.register_close_cb(self.logic.on_end)
        self.logic.on_start()


class GameWindow(Game):

    def __init__(self, classes, conf):
        Game.__init__(self, classes, conf)
        eng.base.run()
