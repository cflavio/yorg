from yyagl.game import GameWindow
from yyagl.dictfile import DictFile
from yyagl.engine.configuration import Configuration
from .logic import YorgLogic
from .event import _Event
from .fsm import _Fsm
from .audio import _Audio


class Yorg(GameWindow):
    logic_cls = YorgLogic
    event_cls = _Event
    fsm_cls = _Fsm
    audio_cls = _Audio

    def __init__(self):
        default_opt = {
            'settings': {
                'lang': 'en',
                'volume': 1,
                'fullscreen': 0,
                'resolution': '1280 720',
                'aa': 0,
                'keys': {
                    'forward': 'arrow_up',
                    'rear': 'z',
                    'left': 'arrow_left',
                    'right': 'arrow_right',
                    'button': 'x'},
                'joystick': 0},
            'development': {
                'multithreaded_render': 0,
                'ai': 0,
                'submodels': 1,
                'split_world': 1,
                'laps': 3,
                'fps': 1,
                'car': '',
                'track': '',
                'shaders': 0,
                'gamma': 2.2,
                'show_waypoints': 0,
                'show_exit': 1,
                'menu_joypad': 1,
                'multiplayer': 0,
                'season': 0,
                'weapons': 0,
                'win_orig': ''}}
        self.options = DictFile('options.yml', default_opt)
        conf = Configuration(
            fps=self.options['development']['fps'],
            win_title='Yorg', win_orig = self.options['development']['win_orig'],
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['aa'],
            lang=self.options['settings']['lang'],
            mt_render=self.options['development']['multithreaded_render'],
            lang_domain='yorg')
        classes = [self.fsm_cls, self.gfx_cls, self.phys_cls, self.gui_cls,
                   YorgLogic, _Audio, self.ai_cls, _Event]
        GameWindow.__init__(self, classes, conf)
