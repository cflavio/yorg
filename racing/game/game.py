""" In this module there will be all classes related
to the game abstract class """
from abc import ABCMeta
from racing.game.gameobject import Logic, GameObjectMdt
import __builtin__


class GameLogic(Logic):
    """ Definition of the Logic Class """

    def run(self):
        pass


class Game(GameObjectMdt):
    """ Definition of the LevelMediator Class """
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self):
        __builtin__.game = self
        GameObjectMdt.__init__(self)

    def run(self):
        self.logic.run()
        eng.run()
