import argparse, sys
from logging import info
from sys import platform, path
from importlib import reload
from copy import deepcopy
from os import walk
from os.path import exists, dirname
from yaml import load
from panda3d.core import Filename
from yyagl.game import Game
from yyagl.dictfile import DctFile
from yyagl.engine.configuration import Cfg, GuiCfg, ProfilingCfg, LangCfg, \
    CursorCfg, DevCfg
from yyagl.engine.gui.menu import MenuProps, NavInfo, NavInfoPerPlayer
from yyagl.engine.logic import EngineLogic
from yyagl.racing.gameprops import GameProps
from yyagl.racing.driver.driver import Driver
from .logic import YorgLogic
from .event import YorgEvent
from .fsm import YorgFsm
from .audio import YorgAudio
from .client import YorgClient
from .thanksnames import ThanksNames
from yyagl.lib.p3d.p3d import LibP3d


class DriverPaths(object):

    def __init__(self, path, path_sel):
        self.path = path
        self.path_sel = path_sel


class DamageInfo(object):

    def __init__(self, low, hi):
        self.low = low
        self.hi = hi


class WheelGfxNames(object):

    def __init__(self, front, rear, both):
        self.front = front
        self.rear = rear
        self.both = both


class Yorg(Game):

    def __init__(self):
        default_opt = {
            'settings': {
                'lang': 'en',
                'volume': 1,
                'fullscreen': 0,
                'resolution': '1280 720',
                'antialiasing': 0,
                'cars_number': 8,
                'keys': {
                    'forward1': 'raw-arrow_up',
                    'rear1': 'raw-arrow_down',
                    'left1': 'raw-arrow_left',
                    'right1': 'raw-arrow_right',
                    'fire1': 'raw-rcontrol',
                    'respawn1': 'raw-rshift',
                    'forward2': 'raw-w',
                    'rear2': 'raw-s',
                    'left2': 'raw-a',
                    'right2': 'raw-d',
                    'fire2': 'raw-x',
                    'respawn2': 'raw-c',
                    'forward3': 'raw-i',
                    'rear3': 'raw-k',
                    'left3': 'raw-j',
                    'right3': 'raw-l',
                    'fire3': 'raw-n',
                    'respawn3': 'raw-m',
                    'forward4': 'raw-t',
                    'rear4': 'raw-g',
                    'left4': 'raw-f',
                    'right4': 'raw-h',
                    'fire4': 'raw-v',
                    'respawn4': 'raw-b',
                    'pause': 'raw-p'},
                'joystick': {
                    'forward1': 'face_x',
                    'rear1': 'face_y',
                    'fire1': 'face_a',
                    'respawn1': 'face_b',
                    'forward2': 'face_x',
                    'rear2': 'face_y',
                    'fire2': 'face_a',
                    'respawn2': 'face_b',
                    'forward3': 'face_x',
                    'rear3': 'face_y',
                    'fire3': 'face_a',
                    'respawn3': 'face_b',
                    'forward4': 'face_x',
                    'rear4': 'face_y',
                    'fire4': 'face_a',
                    'respawn4': 'face_b'},
                'last_version': '0.7.0-x',
                'player_names': [],
                'stored_player_names': [],
                'shaders': 1,
                'camera': 'top',
                'login':
                    {'usr': '', 'pwd': ''}},
            'development': {
                'multithreaded_render': 1,
                'ai': 0,
                'ai_debug': 0,
                'fps': 0,
                'cars': '',
                'track': '',
                'start_wp': '',
                'shaders_dev': 0,
                'gamma': 2.2,
                'show_waypoints': 0,
                'show_exit': 1,
                'menu_joypad': 1,
                'win_orig': '',
                'port': 9099,
                'profiling': 0,
                'pyprof_percall': 0,
                'verbose': '',
                'verbose_log': 0,
                'race_start_time': 3.5,
                'countdown_seconds': 3,
                'xmpp_debug': 0,
                'xmpp_server': 'ya2_yorg@jabb3r.org',
                'server': 'ya2tech.it:9099',
                'mp_srv_usr': '',
                'fixed_fps': 0,
                'srgb': 0,
                'opengl_3_2': 0}}
        opt_path = ''
        if platform in ['win32', 'linux'] and not exists('main.py'):
            # it is the deployed version for windows
            opt_path = str(Filename.get_user_appdata_directory()) + '/Yorg'
        parser = argparse.ArgumentParser()
        parser.add_argument('--win_orig')
        parser.add_argument('--user')
        parser.add_argument('--pwd')
        parser.add_argument('--cars')
        parser.add_argument('--server')
        parser.add_argument('--optfile')
        args = parser.parse_args(EngineLogic.cmd_line())
        optfile = args.optfile if args.optfile else 'options.yml'
        old_def = deepcopy(default_opt)
        self.options = DctFile(
            LibP3d.fixpath(opt_path + '/' + optfile) if opt_path else optfile,
            default_opt)
        if self.options['development']['server'] == '':
            self.options['development']['server'] = old_def['development']['server']
        opt_dev = self.options['development']
        win_orig = opt_dev['win_orig']
        if args.win_orig: win_orig = args.win_orig
        if args.cars: opt_dev['cars'] = args.cars
        if args.server: opt_dev['server'] = args.server
        gui_cfg = GuiCfg(
            win_title='Yorg', win_orig=win_orig,
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['antialiasing'],
            fps=opt_dev['fps'], shaders=self.options['settings']['shaders'],
            volume=self.options['settings']['volume'],
            fixed_fps=self.options['development']['fixed_fps'])
        profiling_cfg = ProfilingCfg(
            profiling=opt_dev['profiling'],
            pyprof_percall=opt_dev['pyprof_percall'])
        lang_cfg = LangCfg(lang=self.options['settings']['lang'],
                           lang_domain='yorg',
                           languages=[('English', 'en'), ('Deutsch', 'de'),
                                      (u'Espa\u00F1ol', 'es'),
                                      (u'Fran\u00E7ais', 'fr'),
                                      (u'G\u00E0idhlig', 'gd'),
                                      ('Galego', 'gl'), ('Italiano', 'it')])
        cursor_cfg = CursorCfg(
            cursor_path='assets/images/gui/cursor.txo',
            cursor_scale=((256/352.0) * .08, 1, .08),
            cursor_hotspot=(.1, .06))
        dev_cfg = DevCfg(
            mt_render=opt_dev['multithreaded_render'],
            shaders_dev=opt_dev['shaders_dev'], gamma=opt_dev['gamma'],
            menu_joypad=opt_dev['menu_joypad'], verbose=opt_dev['verbose'],
            verbose_log=opt_dev['verbose_log'],
            xmpp_server=opt_dev['xmpp_server'],
            start_wp=opt_dev['start_wp'], port=opt_dev['port'],
            server=opt_dev['server'],
            srgb=opt_dev['srgb'],
            opengl_3_2=opt_dev['opengl_3_2'])
        conf = Cfg(gui_cfg, profiling_cfg, lang_cfg, cursor_cfg, dev_cfg)
        keys = self.options['settings']['keys']
        nav1 = NavInfoPerPlayer(keys['left1'], keys['right1'], keys['forward1'],
                                keys['rear1'], keys['fire1'])
        nav2 = NavInfoPerPlayer(keys['left2'], keys['right2'], keys['forward2'],
                                keys['rear2'], keys['fire2'])
        nav3 = NavInfoPerPlayer(keys['left3'], keys['right3'], keys['forward3'],
                                keys['rear3'], keys['fire3'])
        nav4 = NavInfoPerPlayer(keys['left4'], keys['right4'], keys['forward4'],
                                keys['rear4'], keys['fire4'])
        nav = NavInfo([nav1, nav2, nav3, nav4])
        menu_props = MenuProps(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), (.75, .25, .25, 1), .1, (-4.6, 4.6, -.32, .88),
            (0, 0, 0, .2), 'assets/images/gui/menu_background.txo',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s.txo', nav)
        damage_info = DamageInfo('assets/cars/%s/models/cardamage1',
                                 'assets/cars/%s/models/cardamage2')
        Game.__init__(self, conf, YorgClient)
        self.fsm = YorgFsm(self)
        self.logic = YorgLogic(self)
        self.audio = YorgAudio(self)
        self.event = YorgEvent(self)
        cars_names = self.__compute_cars()
        wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
        wheel_gfx_names = [
            self.eng.curr_path + 'assets/cars/%s/models/' + wname
            for wname in wheel_gfx_names]
        wheel_gfx_names = WheelGfxNames(*wheel_gfx_names)
        social_sites = [
            ('facebook', 'https://www.facebook.com/Ya2Tech'),
            ('twitter', 'https://twitter.com/ya2tech'),
            ('google_plus', 'https://plus.google.com/118211180567488443153'),
            ('youtube',
             'https://www.youtube.com/user/ya2games?sub_confirmation=1'),
            ('pinterest', 'https://www.pinterest.com/ya2tech'),
            ('tumblr', 'https://ya2tech.tumblr.com'),
            ('feed', 'https://www.ya2.it/pages/feed-following.html')]
        tracks = self.__compute_tracks()
        tracks_tr = self.__compute_tracks_tr()
        self.gameprops = GameProps(
            menu_props, cars_names, self.drivers(), tracks, tracks_tr,
            'assets/tracks/%s/images/menu.txo',
            self.options['settings']['player_names'],
            self.options['settings']['stored_player_names'],
            DriverPaths('assets/images/drivers/driver%s.txo',
                        'assets/images/drivers/driver%s_sel.txo'),
            'assets/cars/%s/images/car_sel.txo',
            'assets/cars/%s/images/car.txo',
            self.eng.curr_path + 'assets/cars/%s/phys.yml',
            'assets/cars/%s/models/car',
            damage_info, wheel_gfx_names, opt_dev['xmpp_debug'],
            social_sites)
        self.log_conf(self.options.dct)
        self.eng.lib.set_icon('assets/images/icon/yorg.ico')

    def log_conf(self, dct, pref=''):
        for key, val in dct.items():
            if type(val) == dict:
                self.log_conf(val, pref + key + '::')
            elif key != 'pwd':
                info('option %s%s = %s' % (pref, key, val))

    def __compute_tracks(self):
        curr_path = dirname(__file__) + '/'
        if __file__.endswith('.py'): curr_path += '../'
        if sys.platform == 'darwin': curr_path += '../Resources/'
        tracks = [r for r in next(walk(curr_path + 'assets/tracks'))[1] if r not in ['__pycache__', 'models']]
        tracks_i = []
        for track in tracks:
            with open(self.eng.curr_path + 'assets/tracks/' + track + '/track.yml') as ftrack:
                sorting = load(ftrack)['sorting']
            tracks_i += [(track, sorting)]
        tracks_i = sorted(tracks_i, key=lambda elm: elm[1])
        return [track[0] for track in tracks_i]

    def __compute_tracks_tr(self):
        translated = []
        for track in self.__compute_tracks():
            path.insert(0, self.eng.curr_path + 'assets/tracks/' + track)
            mod = __import__('track_tr')
            reload(mod)
            translated += [mod.translated]
            path.pop(0)
        return lambda: translated

    def __compute_cars(self):
        curr_path = dirname(__file__) + '/'
        if __file__.endswith('.py'): curr_path += '../'
        if sys.platform == 'darwin': curr_path += '../Resources/'
        cars = [r for r in next(walk(curr_path + 'assets/cars'))[1]]
        cars_i = []
        for car in cars:
            with open(self.eng.curr_path + 'assets/cars/' + car + '/phys.yml') as fcar:
                sorting = load(fcar)['sorting']
            cars_i += [(car, sorting)]
        cars_i = sorted(cars_i, key=lambda elm: elm[1])
        return [car[0] for car in cars_i]

    def reset_drivers(self):
        self.gameprops.drivers_info = self.drivers()

    def kill(self):
        self.eng.server.destroy()
        self.eng.client.destroy()

    @staticmethod
    def drivers():
        names = ThanksNames.get_thanks(8, 5)
        _drivers = [
            Driver(0, names[0], 4, -2, -2),
            Driver(1, names[1], -2, 4, -2),
            Driver(2, names[2], 0, 4, -4),
            Driver(3, names[3], 4, -4, 0),
            Driver(4, names[4], -2, -2, 4),
            Driver(5, names[5], -4, 0, 4),
            Driver(6, names[6], 4, 0, -4),
            Driver(7, names[7], -4, 4, 0)]
        return _drivers
