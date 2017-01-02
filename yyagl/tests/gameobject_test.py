from mock import patch, create_autospec
from panda3d.core import loadPrcFileData
from unittest import TestCase

from racing.game.engine.engine import Engine
from racing.game.gameobject import Ai, Audio, Event, Fsm, GameObjectMdt, Gfx, Gui, \
    Logic, Phys, Colleague


class AiTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        ai = Ai(game_obj)
        self.assertIsInstance(ai, Ai)


class AudioTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        audio = Audio(game_obj)
        self.assertIsInstance(audio, Audio)


class ColleagueTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        colleague = Colleague(game_obj)
        self.assertIsInstance(colleague, Colleague)


class EventTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        event = Event(game_obj)
        self.assertIsInstance(event, Event)


class FsmTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        fsm = Fsm(game_obj)
        self.assertIsInstance(fsm, Fsm)


class GfxTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        gfx = Gfx(game_obj)
        self.assertIsInstance(gfx, Gfx)


class GuiTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        gui = Gui(game_obj)
        self.assertIsInstance(gui, Gui)


class LogicTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        logic = Logic(game_obj)
        self.assertIsInstance(logic, Logic)


class PhysicsTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    def test_init(self):
        self.engine = Engine()
        game_obj = GameObjectMdt()
        phys = Phys(game_obj)
        self.assertIsInstance(phys, Phys)


class GameObjectTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')
        loadPrcFileData('', 'audio-library-name null')

    def tearDown(self):
        self.engine.destroy()

    @patch.object(Gfx, 'destroy')
    @patch.object(Gui, 'destroy')
    @patch.object(Logic, 'destroy')
    @patch.object(Audio, 'destroy')
    @patch.object(Phys, 'destroy')
    @patch.object(Ai, 'destroy')
    @patch.object(Event, 'destroy')
    @patch.object(Fsm, 'destroy')
    def test_init(
            self, mock_fsm_destroy, mock_event_destroy, mock_ai_destroy,
            mock_phys_destroy, mock_audio_destroy, mock_logic_destroy,
            mock_gui_destroy, mock_gfx_destroy
            ):
        self.engine = Engine()
        mock_event_destroy.__name__ = 'destroy'
        game_obj = GameObjectMdt()
        self.assertIsInstance(game_obj, GameObjectMdt)
        game_obj.destroy()
        assert mock_fsm_destroy.called
        assert mock_event_destroy.called
        assert mock_ai_destroy.called
        assert mock_phys_destroy.called
        assert mock_audio_destroy.called
        assert mock_logic_destroy.called
        assert mock_gui_destroy.called
        assert mock_gfx_destroy.called
