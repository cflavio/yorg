from sys import exit
from yaml import load
from random import shuffle, randint
from os import listdir, remove
from direct.gui.OnscreenText import OnscreenText
from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient
from yyagl.racing.race.raceprops import RaceProps
from yyagl.racing.driver.driver import Driver, DriverProps
from yyagl.gameobject import Fsm
from yyagl.racing.season.season import SingleRaceSeason, Season
from yyagl.engine.gui.menu import MenuArgs
from yyagl.racing.season.season import SeasonProps
from menu.menu import YorgMenu
from menu.exitmenu.menu import ExitMenu
from menu.ingamemenu.menu import InGameMenu


class YorgFsm(Fsm):

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
        eng.log('entering Menu state')
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), .1, (-4.6, 4.6, -.32, .88), (0, 0, 0, .2),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png', (.75, .25, .25, 1))
        sett = self.mdt.options['settings']
        self.__menu = YorgMenu(
            menu_args, self.mdt.options,
            ['kronos', 'themis', 'diones', 'iapeto'],
            'assets/images/cars/%s.png', 'assets/models/cars/%s/phys.yml',
            ['desert', 'mountain'], [_('desert'), _('mountain')],
            'assets/images/tracks/%s.png',
            self.mdt.options['settings']['player_name'],
            ['assets/images/drivers/driver%s.png',
             'assets/images/drivers/driver%s_sel.png'],
            'assets/images/cars/%s_sel.png',
            self.mdt.options['development']['multiplayer'],
            'assets/images/gui/yorg_title.png',
            'http://feeds.feedburner.com/ya2tech?format=xml',
            'http://www.ya2.it', 'save' in self.mdt.options.dct,
            self.mdt.options['development']['season'], ['prototype', 'desert'])
        self.__menu.gui.menu.attach_obs(self.on_input_back)
        self.__menu.gui.menu.attach_obs(self.on_options_back)
        self.__menu.gui.menu.attach_obs(self.on_car_selected)
        self.__menu.gui.menu.attach_obs(self.on_car_selected_season)
        self.__menu.gui.menu.attach_obs(self.on_driver_selected)
        self.__menu.gui.menu.attach_obs(self.on_exit)
        self.__menu.gui.menu.attach_obs(self.on_continue)
        self.mdt.audio.menu_music.play()
        for file_ in [f_ for f_ in listdir('.') if f_.endswith('.bam')]:
            curr_version = eng.version
            file_version = file_[:-4].split('_')[-1]
            if curr_version != file_version:
                eng.log('removing ' + file_)
                remove(file_)
        if self.mdt.logic.season:
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_end)
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_cont)

    def on_input_back(self, dct):
        self.mdt.options['settings'].update(dct)
        self.mdt.options.store()

    def on_options_back(self, dct):
        self.mdt.options['settings'].update(dct)
        self.mdt.options.store()

    def on_car_selected(self, car):
        season_props = SeasonProps(
            ['kronos', 'themis', 'diones', 'iapeto'], car,
            self.mdt.logic.drivers,
            'assets/images/gui/menu_background.jpg',
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            ['prototype', 'desert'],
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .75, 1))
        self.mdt.logic.season = SingleRaceSeason(season_props)
        self.mdt.logic.season.attach_obs(self.mdt.event.on_season_end)
        self.mdt.logic.season.attach_obs(self.mdt.event.on_season_cont)

    def on_car_selected_season(self, car):
        season_props = SeasonProps(
            ['kronos', 'themis', 'diones', 'iapeto'], car, game.logic.drivers,
            'assets/images/gui/menu_background.jpg',
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            ['prototype', 'desert'],
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .75, 1))
        self.mdt.logic.season = Season(season_props)
        self.mdt.logic.season.logic.attach(self.mdt.event.on_season_end)
        self.mdt.logic.season.logic.attach(self.mdt.event.on_season_cont)
        self.mdt.logic.season.logic.start()

    def on_driver_selected(self, player_name, drivers, track, car):
        self.mdt.options['settings']['player_name'] = player_name
        self.mdt.options.store()
        self.mdt.logic.season.drivers = drivers
        args = ['Race', track, car, drivers]
        eng.do_later(2.0, game.fsm.demand, args)

    def on_continue(self):
        season_props = SeasonProps(
            ['kronos', 'themis', 'diones', 'iapeto'],
            self.mdt.options['save']['car'], self.mdt.logic.drivers,
            'assets/images/gui/menu_background.jpg',
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            ['prototype', 'desert'], 'assets/fonts/Hanken-Book.ttf',
            (.75, .75, .75, 1))
        self.mdt.logic.season = Season(season_props)
        self.mdt.logic.season.logic.load(game.options['save']['ranking'],
                                     game.options['save']['tuning'],
                                     game.options['save']['drivers'])
        self.mdt.logic.season.logic.attach(self.mdt.event.on_season_end)
        self.mdt.logic.season.logic.attach(self.mdt.event.on_season_cont)
        track_path = self.mdt.options['save']['track']
        car_path = self.mdt.options['save']['car']
        drivers = self.mdt.options['save']['drivers']
        self.demand('Race', track_path, car_path, drivers)

    def on_exit(self):
        self.demand('Exit')

    def exitMenu(self):
        eng.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', drivers=''):
        eng.log_mgr.log('entering Race state')
        base.ignore('escape-up')
        if 'save' not in self.mdt.options.dct:
            self.mdt.options['save'] = {}
        self.mdt.options['save']['track'] = track_path
        self.mdt.options['save']['car'] = car_path
        self.mdt.options['save']['drivers'] = drivers
        self.mdt.options.store()
        keys = self.mdt.options['settings']['keys']
        joystick = self.mdt.options['settings']['joystick']
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), .1, (-4.6, 4.6, -.32, .88), (0, 0, 0, .2),
            'assets/images/loading/%s%s.jpg' % (track_path, randint(1, 4)),
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg', '',
            (.75, .25, .25, 1))
        sounds = {
            'engine': 'assets/sfx/engine.ogg',
            'brake': 'assets/sfx/brake.ogg',
            'crash': 'assets/sfx/crash.ogg',
            'crash_hs': 'assets/sfx/crash_high_speed.ogg',
            'lap': 'assets/sfx/lap.ogg',
            'landing': 'assets/sfx/landing.ogg'}
        if eng.is_server_active:
            self.race = RaceServer(keys, joystick, sounds)
        elif eng.is_client_active:
            self.race = RaceClient(keys, joystick, sounds)
        else:
            wheel_names = [['EmptyWheelFront', 'EmptyWheelFront.001',
                            'EmptyWheelRear', 'EmptyWheelRear.001'],
                           ['EmptyWheel', 'EmptyWheel.001', 'EmptyWheel.002',
                            'EmptyWheel.003']]
            wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
            wheel_gfx_names = ['assets/models/cars/%s/' + elm
                               for elm in wheel_gfx_names]
            tuning = self.mdt.logic.season.logic.tuning.logic.tunings[car_path]

            def get_driver(car):
                for driver in drivers:
                    if driver[3] == car:
                        return driver
            driver = get_driver(car_path)
            driver_engine, driver_tires, driver_suspensions = driver[2]
            drivers_dct = {}
            for driver in drivers:
                d_s = driver[2]
                driver_props = DriverProps(
                    str(driver[0]), d_s[0], d_s[1], d_s[2])
                drv = Driver(driver_props)
                drivers_dct[driver[3]] = drv
            with open('assets/models/tracks/%s/track.yml' % track_path) as track_file:
                track_conf = load(track_file)
                music_name = track_conf['music']
            music_path = 'assets/music/%s.ogg' % music_name
            corner_names = ['topleft', 'topright', 'bottomright', 'bottomleft']
            corner_names = ['Minimap' + crn for crn in corner_names]
            col_dct = {
                'kronos': (0, 0, 1, 1),
                'themis': (1, 0, 0, 1),
                'diones': (1, 1, 1, 1),
                'iapeto': (1, 1, 0, 1)}
            with open('assets/models/tracks/%s/track.yml' % track_path) as track_file:
                track_cfg = load(track_file)
                camera_vec = track_cfg['camera_vector']
                shadow_src = track_cfg['shadow_source']
                laps = track_cfg['laps']

            def sign_cb(parent):
                thanks = open('assets/thanks.txt').readlines()
                shuffle(thanks)
                text = '\n\n'.join(thanks[:3])
                txt = OnscreenText(text, parent=parent, scale=.2,
                                   fg=(0, 0, 0, 1), pos=(.245, 0))
                bounds = lambda: txt.getTightBounds()
                while bounds()[1][0] - bounds()[0][0] > .48:
                    scale = txt.getScale()[0]
                    txt.setScale(scale - .01, scale - .01)
                bounds = txt.getTightBounds()
                height = bounds[1][2] - bounds[0][2]
                txt.setZ(.06 + height / 2)
            race_props = RaceProps(
                keys, joystick, sounds, (.75, .75, .25, 1), (.75, .75, .75, 1),
                'assets/fonts/Hanken-Book.ttf',
                'assets/models/cars/%s/capsule', 'Capsule',
                'assets/models/cars', 'assets/models/cars/%s/phys.yml',
                wheel_names, tuning.engine, tuning.tires, tuning.suspensions,
                'Road', 'assets/models/cars/%s/car',
                ['assets/models/cars/%s/cardamage1',
                 'assets/models/cars/%s/cardamage2'], wheel_gfx_names,
                'assets/particles/sparks.ptf', drivers_dct,
                game.options['development']['shaders'], music_path,
                'assets/models/tracks/%s/collision' % track_path, ['Road', 'Offroad'],
                ['Wall'], ['Goal', 'Slow', 'Respawn', 'PitStop'],
                corner_names, ['Waypoints', 'Waypoint', 'prev'],
                game.options['development']['show_waypoints'],
                game.options['development']['weapons'],
                ['Weaponboxs', 'EmptyWeaponboxAnim'], 'Start', track_path,
                'tracks/' + track_path, 'track', 'Empty', 'Anim', 'omni',
                sign_cb, 'EmptyNameBillboard4Anim',
                'assets/images/minimaps/%s.png' % track_path,
                'assets/images/minimaps/car_handle.png', col_dct, camera_vec,
                shadow_src, laps, 'assets/models/weapons/rocket/rocket',
                'assets/models/weapons/bonus/WeaponboxAnim', 'Anim',
                ['kronos', 'themis', 'diones', 'iapeto'],
                game.options['development']['ai'], InGameMenu,
                menu_args, 'assets/images/drivers/driver%s_sel.png',
                'assets/images/cars/%s_sel.png',
                ['https://www.facebook.com/sharer/sharer.php?u=ya2.it/yorg',
                 'https://twitter.com/share?text=I%27ve%20achieved%20{time}'
                 '%20in%20the%20{track}%20track%20on%20Yorg%20by%20%40ya2tech'
                 '%21&hashtags=yorg',
                 'https://plus.google.com/share?url=ya2.it/yorg',
                 'https://www.tumblr.com/widgets/share/tool?url=ya2.it'],
                'assets/images/icons/%s_png.png', 'Respawn', 'PitStop',
                'Wall', 'Goal', 'Bonus', ['Road', 'Offroad'],
                ['kronos', 'themis', 'diones', 'iapeto'], car_path)
            #todo compute the grid
            self.race = RaceSinglePlayer(race_props)
        eng.log('selected drivers: ' + str(drivers))
        self.race.logic.drivers = drivers
        track_name_transl = track_path
        track_dct = {'desert': _('desert'), 'mountain': _('mountain')}
        if track_path in track_dct:
            track_name_transl = track_dct[track_path]
        singlerace = game.logic.season.__class__ == SingleRaceSeason
        self.race.fsm.demand(
            'Loading', track_path, car_path, [], drivers,
            ['prototype', 'desert'], track_name_transl, singlerace,
            ['kronos', 'themis', 'diones', 'iapeto'],
            'assets/images/cars/%s_sel.png',
            'assets/images/drivers/driver%s_sel.png',
            game.options['settings']['joystick'],
            game.options['settings']['keys'], menu_args,
            'assets/sfx/countdown.ogg')
        self.race.attach_obs(self.on_race_loaded)
        self.race.attach_obs(self.on_ingame_exit_confirm)

    def on_ingame_exit_confirm(self):
        self.demand('Menu')

    def on_race_loaded(self):
        self.race.event.detach(self.on_race_loaded)
        self.race.results.attach(self.on_race_step)

    def on_race_step(self, race_ranking):
        self.race.results.detach(self.on_race_step)
        ranking = self.mdt.logic.season.ranking
        tuning = self.mdt.logic.season.logic.tuning
        from yyagl.racing.season.season import SingleRaceSeason
        if self.mdt.logic.season.__class__ != SingleRaceSeason:
            for car in ranking.ranking:
                ranking.ranking[car] += race_ranking[car]
            self.mdt.options['save']['ranking'] = ranking.ranking
            self.mdt.options['save']['tuning'] = tuning.logic.tunings
            self.mdt.options.store()
            self.mdt.fsm.demand('Ranking')
        else:
            self.mdt.fsm.demand('Menu')

    def exitRace(self):
        eng.log('exiting Race state')
        self.race.destroy()
        base.accept('escape-up', self.demand, ['Exit'])

    def enterRanking(self):
        self.mdt.logic.season.ranking.show()
        eng.do_later(10, self.mdt.fsm.demand, ['Tuning'])

    def exitRanking(self):
        self.mdt.logic.season.ranking.hide()

    def enterTuning(self):
        self.mdt.logic.season.logic.tuning.gui.show()

    def exitTuning(self):
        self.mdt.logic.season.logic.tuning.gui.hide()

    def enterExit(self):
        if not self.mdt.options['development']['show_exit']:
            exit()
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .25, 1), .1, (-4.6, 4.6, -.32, .88), (0, 0, 0, .2), '',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg', '',
            (.75, .25, .25, 1))
        self.__exit_menu = ExitMenu(menu_args)

    def exitExit(self):
        self.__exit_menu.destroy()
