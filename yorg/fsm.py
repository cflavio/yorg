from yaml import load
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient
from yyagl.racing.driver.driver import Driver
from yyagl.gameobject import Fsm
from menu.menu import YorgMenu
from menu.exitmenu.menu import ExitMenu
import sys
import os


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Race', 'Exit'],
            'Race': ['Ranking', 'Menu', 'Exit'],
            'Ranking': ['Tuning', 'Exit'],
            'Tuning': ['Menu', 'Race', 'Exit'],
            'Exit': ['Exit']}
        self.load_txt = None
        self.preview = None
        self.cam_tsk = None
        self.cam_node = None
        self.ranking_texts = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.curr_load_txt = None
        self.__menu = None
        self.race = None
        self.__exit_menu = None

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = YorgMenu()
        self.mdt.audio.menu_music.play()
        for file_ in os.listdir('.'):
            if file_.endswith('.bam'):
                curr_version = eng.logic.version
                file_version = file_[:-4].split('_')[-1]
                if curr_version != file_version:
                    eng.log_mgr.log('removing ' + file_)
                    os.remove(file_)
        if game.logic.season:
            game.logic.season.logic.detach(game.event.on_season_end)
            game.logic.season.logic.detach(game.event.on_season_cont)

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', player_cars=[],
                  drivers='', skills=''):
        eng.log_mgr.log('entering Race state')
        keys = self.mdt.options['settings']['keys']
        joystick = self.mdt.options['settings']['joystick']
        sounds = {
            'engine': 'assets/sfx/engine.ogg',
            'brake': 'assets/sfx/brake.ogg',
            'crash': 'assets/sfx/crash.ogg',
            'crash_hs': 'assets/sfx/crash_high_speed.ogg',
            'lap': 'assets/sfx/lap.ogg',
            'landing': 'assets/sfx/landing.ogg'}
        if eng.server.is_active:
            self.race = RaceServer(keys, joystick, sounds)
        elif eng.client.is_active:
            self.race = RaceClient(keys, joystick, sounds)
        else:
            wheel_names = [['EmptyWheelFront', 'EmptyWheelFront.001',
                            'EmptyWheelRear', 'EmptyWheelRear.001'],
                           ['EmptyWheel', 'EmptyWheel.001', 'EmptyWheel.002',
                            'EmptyWheel.003']]
            tuning = self.mdt.logic.season.logic.tuning.logic.tunings[car_path]
            def get_driver(car):
                for driver in drivers:
                    if driver[2] == car:
                        return driver
            driver_engine, driver_tires, driver_suspensions = skills[get_driver(car_path)[0] - 1]
            drivers_dct = {}
            for driver in drivers:
                d_s = skills[get_driver(driver[2])[0] - 1]
                drv = Driver(str(driver[0]), d_s[0], d_s[1], d_s[2])
                drivers_dct[driver[2]] = drv
            with open('assets/models/%s/track.yml' % track_path) as track_file:
                track_conf = load(track_file)
                music_name = track_conf['music']
            music_path = 'assets/music/%s.ogg' % music_name
            corner_names = ['topleft', 'topright', 'bottomright', 'bottomleft']
            corner_names = ['Minimap' + crn for crn in corner_names]
            thanks = open('assets/thanks.txt').readlines()
            col_dct = {
                'kronos': (0, 0, 1, 1),
                'themis': (1, 0, 0, 1),
                'diones': (1, 1, 1, 1),
                'iapeto': (1, 1, 0, 1)}
            with open('assets/models/%s/track.yml' % track_path) as track_file:
                track_cfg = load(track_file)
                camera_vec = track_cfg['camera_vector']
                shadow_src = track_cfg['shadow_source']
                laps = track_cfg['laps']
            self.race = RaceSinglePlayer(
                keys, joystick, sounds, (.75, .75, .25, 1), (.75, .75, .75, 1),
                'assets/fonts/Hanken-Book.ttf', 'capsule', 'Capsule',
                'assets/models/cars', 'phys.yml', wheel_names,
                tuning.engine, tuning.tires, tuning.suspensions,
                'Road', 'assets/models/cars', 'car',
                ['cardamage1', 'cardamage2'],
                ['wheelfront', 'wheelrear', 'wheel'],
                'assets/particles/sparks.ptf', drivers_dct,
                game.options['development']['shaders'], music_path,
                'assets/models/%s/collision' % track_path, ['Road', 'Offroad'],
                ['Wall'], ['Goal', 'Slow', 'Respawn', 'PitStop'],
                corner_names, ['Waypoints', 'Waypoint', 'prev'],
                game.options['development']['show_waypoints'],
                game.options['development']['weapons'],
                ['Weaponboxs', 'EmptyWeaponboxAnim'], 'Start', track_path[7:],
                 track_path, 'track', 'Empty', 'Anim', 'omni',
                 thanks, 'EmptyNameBillboard4Anim', 'assets/images/minimaps',
                 'car_handle.png', col_dct, camera_vec, shadow_src, laps,
                 'assets/models/weapons/rocket/rocket',
                 'assets/models/weapons/bonus/WeaponboxAnim', 'Anim')
            # use global template args
        eng.log_mgr.log('selected drivers: ' + str(drivers))
        self.race.logic.drivers = drivers
        self.race.fsm.demand('Loading', track_path, car_path, player_cars,
                             drivers)

    def exitRace(self):
        eng.log_mgr.log('exiting Race state')
        self.race.destroy()

    def enterRanking(self):
        game.logic.season.logic.ranking.gui.show()
        to_tun = lambda task: game.fsm.demand('Tuning')
        taskMgr.doMethodLater(10, to_tun, 'tuning')

    def exitRanking(self):
        game.logic.season.logic.ranking.gui.hide()

    def enterTuning(self):
        game.logic.season.logic.tuning.gui.show()

    def exitTuning(self):
        game.logic.season.logic.tuning.gui.hide()

    def enterExit(self):
        if not game.options['development']['show_exit']:
            sys.exit()
        self.__exit_menu = ExitMenu()

    def exitExit(self):
        self.__exit_menu.destroy()
