from collections import namedtuple
from sys import platform
from os.path import join, exists
from panda3d.core import Filename
from yyagl.game import Game
from yyagl.dictfile import DctFile
from yyagl.engine.configuration import Cfg, GuiCfg, ProfilingCfg, LangCfg, \
    CursorCfg, DevCfg
from yyagl.engine.gui.menu import MenuArgs
from yyagl.racing.gameprops import GameProps
from yyagl.racing.driver.driver import DriverInfo
from .logic import YorgLogic
from .event import YorgEvent
from .fsm import YorgFsm
from .audio import YorgAudio
from .thanksnames import ThanksNames


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
                'pyprof_percall': 0,
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
        gui_cfg = GuiCfg(win_title='Yorg', win_orig=opt_dev['win_orig'],
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['antialiasing'],
            fps=opt_dev['fps'], volume=self.options['settings']['volume'])
        profiling_cfg = ProfilingCfg(profiling=opt_dev['profiling'],
            pyprof_percall=opt_dev['pyprof_percall'])
        lang_cfg = LangCfg(lang=self.options['settings']['lang'],
                           lang_domain='yorg', languages=['English', 'Italiano', 'Deutsch'])
        cursor_cfg = CursorCfg(cursor_path='assets/images/gui/cursor.txo',
            cursor_scale=((256/352.0) * .08, 1, .08),
            cursor_hotspot=(.1, .06))
        dev_cfg = DevCfg(mt_render=opt_dev['multithreaded_render'],
            shaders_dev=opt_dev['shaders_dev'], gamma=opt_dev['gamma'],
            menu_joypad=opt_dev['menu_joypad'])
        conf = Cfg(gui_cfg, profiling_cfg, lang_cfg, cursor_cfg, dev_cfg)
        init_lst = [
            [('fsm', YorgFsm, [self])],
            [('logic', YorgLogic, [self])],
            [('audio', YorgAudio, [self])],
            [('event', YorgEvent, [self])]]
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), (.75, .25, .25, 1), .1, (-4.6, 4.6, -.32, .88),
            (0, 0, 0, .2), 'assets/images/gui/menu_background.txo',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s.txo')
        cars_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                      'iperion', 'teia']
        DriverPaths = namedtuple('DriverPaths', 'path path_sel')
        DamageInfo = namedtuple('DamageInfo', 'low hi')
        damage_info = DamageInfo('assets/models/cars/%s/cardamage1',
                                 'assets/models/cars/%s/cardamage2')
        Game.__init__(self, init_lst, conf)
        wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
        wheel_gfx_names = [
            self.eng.curr_path + 'assets/models/cars/%s/' + wname
            for wname in wheel_gfx_names]
        WheelGfxNames = namedtuple('WheelGfxNames', 'front rear both')
        wheel_gfx_names = WheelGfxNames(*wheel_gfx_names)
        self.gameprops = GameProps(
            menu_args, cars_names, self.drivers(),
            ['rome', 'sheffield', 'orlando', 'nagano', 'dubai'],
            lambda: [_('Rome'), _('Sheffield'), _('Orlando'),
                     _('Nagano'), _('Dubai')],
            'assets/images/tracks/%s.txo',
            self.options['settings']['player_name'],
            DriverPaths('assets/images/drivers/driver%s.txo',
                        'assets/images/drivers/driver%s_sel.txo'),
            'assets/images/cars/%s_sel.txo',
            'assets/images/cars/%s.txo',
            self.eng.curr_path + 'assets/models/cars/%s/phys.yml',
            'assets/models/cars/%s/car',
            damage_info, wheel_gfx_names,)

    @staticmethod
    def drivers():
        names = ThanksNames.get_thanks(8, 5)
        _drivers = [
            DriverInfo(0, names[0], 4, -2, -2),
            DriverInfo(1, names[1], -2, 4, -2),
            DriverInfo(2, names[2], 0, 4, -4),
            DriverInfo(3, names[3], 4, -4, 0),
            DriverInfo(4, names[4], -2, -2, 4),
            DriverInfo(5, names[5], -4, 0, 4),
            DriverInfo(6, names[6], 4, 0, -4),
            DriverInfo(7, names[7], -4, 4, 0)]
        return _drivers
