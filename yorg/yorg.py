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
                'antialiasing': 0,
                'cars_number': 7,
                'keys': {
                    'forward': 'arrow_up',
                    'rear': 'arrow_down',
                    'left': 'arrow_left',
                    'right': 'arrow_right',
                    'fire': 'space',
                    'respawn': 'r',
                    'pause': 'p'},
                'joystick': 0,
                'last_version': '0.7.0-x',
                'player_name': '',
                'shaders': 1},
            'development': {
                'multithreaded_render': 0,
                'ai': 0,
                'fps': 0,
                'car': '',
                'track': '',
                'shaders_dev': 0,
                'gamma': 2.2,
                'show_waypoints': 0,
                'show_exit': 1,
                'menu_joypad': 1,
                'multiplayer': 0,
                'win_orig': '',
                'profiling': 0,
                'python_profiling': 0,
                'python_profiling_percall': 0}}
        opt_path = ''
        if platform == 'win32' and not exists('main.py'):
            opt_path = join(str(Filename.get_user_appdata_directory()), 'Yorg')
        self.options = DctFile(
            join(opt_path, 'options.yml') if opt_path else 'options.yml',
            default_opt)
        opt_dev = self.options['development']
        conf = Cfg(
            win_title='Yorg', win_orig=opt_dev['win_orig'],
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['antialiasing'],
            fps=opt_dev['fps'], mt_render=opt_dev['multithreaded_render'],
            shaders_dev=opt_dev['shaders_dev'], gamma=opt_dev['gamma'],
            menu_joypad=opt_dev['menu_joypad'],
            lang=self.options['settings']['lang'], lang_domain='yorg',
            cursor_path='assets/images/gui/cursor.png',
            cursor_scale=((256/352.0) * .08, 1, .08), cursor_hotspot=(.1, .06),
            volume=self.options['settings']['volume'],
            profiling=opt_dev['profiling'],
            python_profiling=opt_dev['python_profiling'],
            python_profiling_percall=opt_dev['python_profiling_percall'])
        init_lst = [
            [('fsm', YorgFsm, [self])],
            [('logic', YorgLogic, [self])],
            [('audio', YorgAudio, [self])],
            [('event', YorgEvent, [self])]]
        Game.__init__(self, init_lst, conf)