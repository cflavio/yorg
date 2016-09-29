""" In this module there will be all classes related
to the game abstract class """
from abc import ABCMeta
from racing.game.gameobject import Logic, GameObjectMdt
from .engine import Engine
import __builtin__


class GameLogic(Logic):
    """ Definition of the Logic Class """

    def run(self):
        '''Starts the game logic.'''
        pass


class Game(GameObjectMdt):
    """ Definition of the LevelMediator Class """
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self, conf, domain):
        __builtin__.game = self
        Engine(conf, domain)
        GameObjectMdt.__init__(self)

    def run(self):
        '''Starts the game.'''
        self.logic.run()
        eng.run()
