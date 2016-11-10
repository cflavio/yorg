from direct.showbase.DirectObject import DirectObject
from mock import create_autospec
from panda3d.core import loadPrcFileData, NodePath, ConfigVariableBool,\
    MouseWatcher, Lens
from unittest import TestCase

from racing.game.engine.engine import Engine
from racing.game.engine.configuration import Configuration


class ConfigurationTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine(Configuration(cursor_hidden=True))
        self.assertTrue(ConfigVariableBool('cursor-hidden'))
        self.assertFalse(ConfigVariableBool('fullscreen'))


class EngineTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        self.engine.camera = create_autospec(NodePath)
        self.assertIsInstance(self.engine, Engine)
        self.engine.toggle_debug()


class Accepter(DirectObject):

    def __init__(self):
        self = evt_dec(self)

    def evt_MouseClick(self, arg):
        self.button = arg.button, 0

    def evt_MouseClickUp(self, arg):
        self.button = arg.button, 1


# class EventsTests(TestCase):
#
#     def setUp(self):
#         loadPrcFileData('', 'window-type none')
#         self.engine = Engine()
#         self.engine.mouseWatcherNode = create_autospec(MouseWatcher)
#         self.engine.camLens = create_autospec(Lens)
#         self.engine.camera = create_autospec(NodePath)
#         self.engine.cam = NodePath()
#
#     def tearDown(self):
#         self.engine.destroy()
#
#     def test_init(self):
#         self.assertIsInstance(self.engine, Engine)
#         mouse_move = MouseMove(0, 0)
#         self.assertIsInstance(mouse_move, MouseMove)
#         mouse_enter = MouseEnter(0, 0)
#         self.assertIsInstance(mouse_enter, MouseEnter)
#         mouse_exit = MouseExit(0, 0, 0)
#         self.assertIsInstance(mouse_exit, MouseExit)
#         mouse_click = MouseClick(0, 0, 0)
#         self.assertIsInstance(mouse_click, MouseClick)
#         mouse_clickup = MouseClickUp(0, 0, 0)
#         self.assertIsInstance(mouse_clickup, MouseClickUp)
#         mouse_mgr = MouseMgr(self.engine)
#         self.assertIsInstance(mouse_mgr, MouseMgr)
#         self.assertEqual(mouse_mgr.pt_from_to, (0, 0))
#         self.assertEqual(mouse_mgr.pt_from, (0, 0, 0))
#         self.assertEqual(mouse_mgr.pt_to, (0, 0, 0))
#         acc = Accepter()
#         self.engine.messenger.send('mouse1')
#         self.assertEqual(acc.button, (0, 0))
#         self.engine.messenger.send('mouse1-up')
#         self.assertEqual(acc.button, (0, 1))
#         self.engine.messenger.send('mouse3')
#         self.assertEqual(acc.button, (1, 0))
#         self.engine.messenger.send('mouse3-up')
#         self.assertEqual(acc.button, (1, 1))
