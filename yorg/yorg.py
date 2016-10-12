'''In this module we define the global game classes.'''
from racing.game.game import Game
from racing.game.dictfile import DictFile
from racing.game.engine.configuration import Configuration
from .logic import _Logic
from .event import _Event
from .fsm import _Fsm
from .audio import _Audio


class Yorg(Game):
    '''This class defines Yorg.'''
    logic_cls = _Logic
    event_cls = _Event
    fsm_cls = _Fsm
    audio_cls = _Audio

    def __init__(self):
        default_opt = {
            'lang': 'en', 'volume': 1, 'fullscreen': 0,
            'resolution': '1280 720', 'aa': 0,
            'multithreaded_render': 0, 'open_browser_at_exit': 1,
            'ai': 0, 'submodels': 1, 'split_world': 1, 'laps': 3, 'fps': 1}
        self.options = DictFile('options.yml', default_opt)
        conf = Configuration(
            fps=self.options['fps'], win_title='Yorg',
            win_size=self.options['resolution'],
            fullscreen=self.options['fullscreen'],
            antialiasing=self.options['aa'], lang=self.options['lang'],
            mt_render=self.options['multithreaded_render'], lang_domain='yorg')
        Game.__init__(self, conf)
