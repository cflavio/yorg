import argparse
from sys import platform
from copy import deepcopy
from os.path import join, exists
from panda3d.core import Filename
from yyagl.game import Game
from yyagl.dictfile import DctFile
from yyagl.engine.configuration import Cfg, GuiCfg, ProfilingCfg, LangCfg, \
    CursorCfg, DevCfg
from yyagl.engine.gui.menu import MenuArgs, NavInfo
from yyagl.racing.gameprops import GameProps
from yyagl.racing.driver.driver import DriverInfo
from .logic import YorgLogic
from .event import YorgEvent
from .fsm import YorgFsm
from .audio import YorgAudio
from .thanksnames import ThanksNames


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
                'cars_number': 7,
                'keys': {
                    'forward1': 'arrow_up',
                    'rear1': 'arrow_down',
                    'left1': 'arrow_left',
                    'right1': 'arrow_right',
                    'fire1': 'm',
                    'respawn1': 'n',
                    'forward2': 'w',
                    'rear2': 's',
                    'left2': 'a',
                    'right2': 'd',
                    'fire2': 't',
                    'respawn2': 'r',
                    'pause': 'p'},
                'joystick1': 0,
                'joystick2': 0,
                'last_version': '0.7.0-x',
                'player_name': '',
                'shaders': 1,
                'camera': 'top',
                'login':
                    {'usr': '', 'pwd': ''}},
            'development': {
                'multithreaded_render': 0,
                'ai': 0,
                'fps': 0,
                'car': '',
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
                'mp_srv_usr': ''}}
        opt_path = ''
        if platform == 'win32' and not exists('main.py'):
            # it is the deployed version for windows
            opt_path = join(str(Filename.get_user_appdata_directory()), 'Yorg')
        parser = argparse.ArgumentParser()
        parser.add_argument('--win_orig')
        parser.add_argument('--user')
        parser.add_argument('--pwd')
        parser.add_argument('--car')
        parser.add_argument('--server')
        parser.add_argument('--optfile')
        args = parser.parse_args()
        optfile = args.optfile if args.optfile else 'options.yml'
        old_def = deepcopy(default_opt)
        self.options = DctFile(
            join(opt_path, optfile) if opt_path else optfile, default_opt)
        if self.options['development']['server'] == '':
            self.options['development']['server'] = old_def['development']['server']
        opt_dev = self.options['development']
        win_orig = opt_dev['win_orig']
        if args.win_orig: win_orig = args.win_orig
        if args.car: opt_dev['car'] = args.car
        if args.server: opt_dev['server'] = args.server
        gui_cfg = GuiCfg(
            win_title='Yorg', win_orig=win_orig,
            win_size=self.options['settings']['resolution'],
            fullscreen=self.options['settings']['fullscreen'],
            antialiasing=self.options['settings']['antialiasing'],
            fps=opt_dev['fps'], shaders=self.options['settings']['shaders'],
            volume=self.options['settings']['volume'])
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
            server=opt_dev['server'])
        conf = Cfg(gui_cfg, profiling_cfg, lang_cfg, cursor_cfg, dev_cfg)
        init_lst = [
            [('fsm', YorgFsm, [self])],
            [('logic', YorgLogic, [self])],
            [('audio', YorgAudio, [self])],
            [('event', YorgEvent, [self])]]
        keys = self.options['settings']['keys']
        nav = NavInfo(keys['left1'], keys['right1'], keys['forward1'],
                      keys['rear1'], keys['fire1'])
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), (.75, .25, .25, 1), .1, (-4.6, 4.6, -.32, .88),
            (0, 0, 0, .2), 'assets/images/gui/menu_background.txo',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s.txo', nav)
        cars_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                      'iperion', 'teia']
        damage_info = DamageInfo('assets/models/cars/%s/cardamage1',
                                 'assets/models/cars/%s/cardamage2')
        Game.__init__(self, init_lst, conf)
        wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
        wheel_gfx_names = [
            self.eng.curr_path + 'assets/models/cars/%s/' + wname
            for wname in wheel_gfx_names]
        wheel_gfx_names = WheelGfxNames(*wheel_gfx_names)
        social_sites = [
            ('facebook', 'http://www.facebook.com/Ya2Tech'),
            ('twitter', 'http://twitter.com/ya2tech'),
            ('google_plus', 'https://plus.google.com/118211180567488443153'),
            ('youtube',
             'http://www.youtube.com/user/ya2games?sub_confirmation=1'),
            ('pinterest', 'http://www.pinterest.com/ya2tech'),
            ('tumblr', 'http://ya2tech.tumblr.com'),
            ('feed', 'http://www.ya2.it/pages/feed-following.html')]
        self.gameprops = GameProps(
            menu_args, cars_names, self.drivers(),
            ['moon', 'toronto', 'rome', 'sheffield', 'orlando', 'nagano',
             'dubai'],
            lambda: [_('Sinus Aestuum'), _('Toronto'), _('Rome'), _('Sheffield'),
                     _('Orlando'), _('Nagano'), _('Dubai')],
            'assets/images/tracks/%s.txo',
            self.options['settings']['player_name'],
            DriverPaths('assets/images/drivers/driver%s.txo',
                        'assets/images/drivers/driver%s_sel.txo'),
            'assets/images/cars/%s_sel.txo',
            'assets/images/cars/%s.txo',
            self.eng.curr_path + 'assets/models/cars/%s/phys.yml',
            'assets/models/cars/%s/car',
            damage_info, wheel_gfx_names, opt_dev['xmpp_debug'],
            social_sites)
        self.log_conf(self.options.dct)

    def log_conf(self, dct, pref=''):
        for key, val in dct.items():
            if type(val) == dict:
                self.log_conf(val, pref + key + '::')
            elif key != 'pwd':
                self.eng.log('option %s%s = %s' % (pref, key, val))

    def reset_drivers(self):
        self.gameprops.drivers_info = self.drivers()

    def kill(self):
        self.eng.xmpp.disconnect()
        self.eng.server.destroy()
        self.eng.client.destroy()

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
