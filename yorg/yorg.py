from collections import namedtuple
from sys import platform
from os.path import join, exists
from panda3d.core import Filename
from yyagl.game import Game
from yyagl.dictfile import DctFile
from yyagl.engine.configuration import Cfg
from yyagl.engine.gui.menu import MenuArgs
from yyagl.racing.gameprops import GameProps
from .logic import YorgLogic
from .event import YorgEvent
from .fsm import YorgFsm
from .audio import YorgAudio
from .thanksnames import ThanksNames


DriverInfo = namedtuple('DriverInfo', 'car_id name skill car_name')
DriverSkill = namedtuple('DriverSkill', 'speed adherence stability')


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
                'python_profiling_percall': 0,
                'race_start_time': 3.5,
                'countdown_seconds': 3}}
        opt_path = ''
        if platform == 'win32' and not exists('main.py'):
            # it is the deployed version for windows
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
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), (.75, .25, .25, 1), .1, (-4.6, 4.6, -.32, .88),
            (0, 0, 0, .2), 'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')
        cars_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                      'iperion', 'teia']
        DriverPaths = namedtuple('DriverPaths', 'path path_sel')
        Game.__init__(self, init_lst, conf)
        self.gameprops = GameProps(
            menu_args, cars_names, self.drivers(),
            ['desert', 'mountain', 'amusement', 'countryside'],
            lambda: [_('desert'), _('mountain'), _('amusement park'),
                     _('countryside')],
            'assets/images/tracks/%s.png',
            self.options['settings']['player_name'],
            DriverPaths('assets/images/drivers/driver%s.png',
                        'assets/images/drivers/driver%s_sel.png'),
            'assets/images/cars/%s_sel.png',
            'assets/images/cars/%s.png',
            self.eng.curr_path + 'assets/models/cars/%s/phys.yml')
        self.run()

    def drivers(self):
        names = ThanksNames.get_thanks(8, 5)
        drivers = [
            DriverInfo(1, names[0], DriverSkill(4, -2, -2), 'themis'),
            DriverInfo(2, names[1], DriverSkill(-2, 4, -2), 'kronos'),
            DriverInfo(3, names[2], DriverSkill(0, 4, -4), 'diones'),
            DriverInfo(4, names[3], DriverSkill(4, -4, 0), 'iapeto'),
            DriverInfo(5, names[4], DriverSkill(-2, -2, 4), 'phoibe'),
            DriverInfo(6, names[5], DriverSkill(-4, 0, 4), 'rea'),
            DriverInfo(7, names[6], DriverSkill(4, 0, -4), 'iperion'),
            DriverInfo(8, names[7], DriverSkill(-4, 4, 0), 'teia')]
        return drivers
