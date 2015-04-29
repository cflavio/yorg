""" In this module there will be all classes related
to the game abstract class """
from abc import ABCMeta
from ya2.gameobject import Logic, GameObjectMdt


class GameLogic(Logic):
    """ Definition of the Logic Class """

    def run(self):
        pass


class Game(GameObjectMdt):
    """ Definition of the LevelMediator Class """
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def run(self):
        self.logic.run()
        eng.run()
