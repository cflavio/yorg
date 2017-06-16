from sys import platform
from os.path import join, exists
from panda3d.core import Filename
from yyagl.game import Game
from yyagl.dictfile import DctFile
from yyagl.engine.configuration import Cfg
from .logic import YorgLogic
from .event import YorgEvent
from .fsm import YorgFsm
from .audio import YorgAudio


class Yorg(Game):

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
                    'button': 'x',
                    'respawn': 'r'},
                'joystick': 0,
                'player_name': ''},
            'development': {
                'multithreaded_render': 0,
                'ai': 0,
                'fps': 0,
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
                'win_orig': '',
                'profiling': 0,
                'python_profiling': 0}}
        opt_path = ''
        if platform == 'win32' and not exists('main.py'):
            opt_path = join(str(Filename.get_user_appdata_directory()), 'Yorg')
        self.options = DctFile(join(opt_path, 'options.yml') if opt_path else 'options.yml', default_opt)
        conf = Cfg(
            win_title='Yorg',
            win_orig=self.options['development']['win_orig'],
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['aa'],
            fps=self.options['development']['fps'],
            mt_render=self.options['development']['multithreaded_render'],
            shaders=self.options['development']['shaders'],
            gamma=self.options['development']['gamma'],
            menu_joypad=self.options['development']['menu_joypad'],
            lang=self.options['settings']['lang'],
            lang_domain='yorg',
            cursor_path='assets/images/gui/cursor.png',
            cursor_scale=((256/352.0) * .08, 1, .08),
            cursor_hotspot=(.1, .06),
            volume=self.options['settings']['volume'],
            profiling=self.options['development']['profiling'],
            python_profiling=self.options['development']['python_profiling'])
        init_lst = [
            [('fsm', YorgFsm, [self])],
            [('logic', YorgLogic, [self])],
            [('audio', YorgAudio, [self])],
            [('event', YorgEvent, [self])]]
        Game.__init__(self, init_lst, conf)
