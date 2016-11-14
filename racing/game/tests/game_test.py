from mock import create_autospec
from os import chdir, getcwd
from panda3d.core import loadPrcFileData, NodePath
from unittest import TestCase
from racing.game.engine.engine import Engine
from racing.game.engine.configuration import Configuration
from racing.game.game import GameLogic, Game
from racing.game.gameobject import GameObjectMdt, Fsm, Gfx, Phys, Gui, Audio, \
    Ai, Event


class LogicTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.eng.destroy()

    def test_init(self):
        self.eng = Engine()
        game_obj = GameObjectMdt()
        logic = GameLogic(game_obj)
        self.assertIsInstance(logic, GameLogic)


class GameTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def test_init(self):
        conf = Configuration()
        classes = [Fsm, Gfx, Phys, Gui, GameLogic, Audio, Ai, Event]
        game = Game(classes, conf)
        self.assertIsInstance(game, Game)
        game.destroy()

    def tearDown(self):
        eng.destroy()
