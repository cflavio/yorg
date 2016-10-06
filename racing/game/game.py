""" In this module there will be all classes related
to the game abstract class """
from abc import ABCMeta
from racing.game.gameobject import Logic, GameObjectMdt
from .engine import Engine
import __builtin__


class GameLogic(Logic):
    """ Definition of the Logic Class """

    def on_start(self):
        '''Called at the start.'''
        pass

    def on_frame(self):
        '''Called on each frame.'''
        pass

    def on_end(self):
        '''Called at the end.'''
        pass


class Game(GameObjectMdt):
    """ Definition of the LevelMediator Class """
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self, conf):
        __builtin__.game = self
        eng = Engine(conf)
        GameObjectMdt.__init__(self)
        eng.gui_mgr.register_close_cb(self.logic.on_end)
        self.logic.on_start()
        eng.attach(self, self.logic.on_frame)
        eng.run()
