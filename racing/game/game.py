""" In this module there will be all classes related
to the game abstract class """
from abc import ABCMeta
from racing.game.gameobject import Logic, GameObjectMdt
from .engine import Engine
import __builtin__


class GameLogic(Logic):
    """ Definition of the Logic Class """

    def start(self):
        '''Starts the game logic.'''
        pass


class Game(GameObjectMdt):
    """ Definition of the LevelMediator Class """
    __metaclass__ = ABCMeta
    logic_cls = GameLogic

    def __init__(self, conf, lang_path, domain, langs):
        __builtin__.game = self
        Engine(conf, lang_path, domain, langs)
        GameObjectMdt.__init__(self)
        self.logic.start()
        eng.run()
