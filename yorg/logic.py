from yaml import load
from os import listdir, remove
from random import shuffle
from direct.gui.OnscreenText import OnscreenText
from yyagl.game import GameLogic
from yyagl.racing.season.season import SingleRaceSeason, Season
from yyagl.racing.driver.driver import Driver, DriverProps
from yyagl.racing.race.raceprops import RaceProps
from menu.ingamemenu.menu import InGameMenu
from .utils import Utils


class YorgLogic(GameLogic):

    def __init__(self, mdt):
        GameLogic.__init__(self, mdt)
        self.season = None

    def on_start(self):
        GameLogic.on_start(self)
        dev = self.mdt.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        if car and track:
            self.season = SingleRaceSeason(Utils().season_props(car))
            self.season.attach_obs(self.mdt.event.on_season_end)
            self.season.attach_obs(self.mdt.event.on_season_cont)
            self.mdt.fsm.demand('Race', track, car, self.season.drivers)
        else:
            self.mdt.fsm.demand('Menu')

    def menu_start(self):
        self.mdt.audio.menu_music.play()
        for file_ in [f_ for f_ in listdir('.') if f_.endswith('.bam')]:
            curr_version = eng.version
            file_version = file_[:-4].split('_')[-1]
            if curr_version != file_version:
                eng.log('removing ' + file_)
                remove(file_)

    def on_input_back(self, dct):
        self.mdt.options['settings'].update(dct)
        self.mdt.options.store()

    def on_options_back(self, dct):
        self.mdt.options['settings'].update(dct)
        self.mdt.options.store()

    def on_car_selected(self, car):
        self.season = SingleRaceSeason(Utils().season_props(car))
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)

    def on_car_selected_season(self, car):
        self.season = Season(Utils().season_props(car))
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)
        self.season.start()

    def on_driver_selected(self, player_name, drivers, track, car):
        self.mdt.options['settings']['player_name'] = player_name
        self.mdt.options.store()
        eng.do_later(2.0, self.mdt.fsm.demand, ['Race', track, car, drivers])

    def on_continue(self):
        saved_car = self.mdt.options['save']['car']
        self.season = Season(Utils().season_props(saved_car))
        self.season.load(self.mdt.options['save']['ranking'],
                         self.mdt.options['save']['tuning'],
                         self.mdt.options['save']['drivers'])
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)
        track_path = self.mdt.options['save']['track']
        car_path = self.mdt.options['save']['car']
        drivers = self.mdt.options['save']['drivers']
        self.mdt.fsm.demand('Race', track_path, car_path, drivers)

    def on_exit(self):
        self.mdt.fsm.demand('Exit')

    def on_ingame_exit_confirm(self):
        self.mdt.fsm.demand('Menu')

    def on_race_loaded(self):
        self.season.race.event.detach(self.on_race_loaded)
        self.season.race.results.attach(self.on_race_step)

    def on_race_step(self, race_ranking):
        self.season.race.results.detach(self.on_race_step)
        ranking = self.season.ranking
        tuning = self.season.tuning
        from yyagl.racing.season.season import SingleRaceSeason
        if self.season.__class__ != SingleRaceSeason:
            for car in ranking.ranking:
                ranking.ranking[car] += race_ranking[car]
            self.mdt.options['save']['ranking'] = ranking.ranking
            self.mdt.options['save']['tuning'] = tuning.tunings
            self.mdt.options.store()
            self.mdt.fsm.demand('Ranking')
        else:
            self.mdt.fsm.demand('Menu')

    def build_race_props(self, car_path, drivers, track_path, keys, joystick,
                         sounds):
        wheel_names = [['EmptyWheelFront', 'EmptyWheelFront.001',
                        'EmptyWheelRear', 'EmptyWheelRear.001'],
                       ['EmptyWheel', 'EmptyWheel.001', 'EmptyWheel.002',
                        'EmptyWheel.003']]
        wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
        wheel_gfx_names = ['assets/models/cars/%s/' + elm
                           for elm in wheel_gfx_names]
        tuning = self.mdt.logic.season.tuning.tunings[car_path]

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
        tr_file_path = 'assets/models/tracks/%s/track.yml' % track_path
        with open(tr_file_path) as track_file:
            music_name = load(track_file)['music']
        music_path = 'assets/music/%s.ogg' % music_name
        corner_names = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corner_names = ['Minimap' + crn for crn in corner_names]
        col_dct = {'kronos': (0, 0, 1, 1), 'themis': (1, 0, 0, 1),
                   'diones': (1, 1, 1, 1), 'iapeto': (1, 1, 0, 1)}
        with open(tr_file_path) as track_file:
            track_cfg = load(track_file)
            camera_vec = track_cfg['camera_vector']
            shadow_src = track_cfg['shadow_source']
            laps = track_cfg['laps']

        def sign_cb(parent):
            thanks = open('assets/thanks.txt').readlines()
            shuffle(thanks)
            text = '\n\n'.join(thanks[:3])
            txt = OnscreenText(text, parent=parent, scale=.2, fg=(0, 0, 0, 1),
                               pos=(.245, 0))
            bounds = lambda: txt.getTightBounds()
            while bounds()[1][0] - bounds()[0][0] > .48:
                scale = txt.getScale()[0]
                txt.setScale(scale - .01, scale - .01)
            bounds = txt.getTightBounds()
            height = bounds[1][2] - bounds[0][2]
            txt.setZ(.06 + height / 2)
        race_props = RaceProps(
            keys, joystick, sounds, (.75, .75, .25, 1), (.75, .75, .75, 1),
            'assets/fonts/Hanken-Book.ttf', 'assets/models/cars/%s/capsule',
            'Capsule', 'assets/models/cars', 'assets/models/cars/%s/phys.yml',
            wheel_names, tuning.engine, tuning.tires, tuning.suspensions,
            'Road', 'assets/models/cars/%s/car',
            ['assets/models/cars/%s/cardamage1',
             'assets/models/cars/%s/cardamage2'], wheel_gfx_names,
            'assets/particles/sparks.ptf', drivers_dct,
            self.mdt.options['development']['shaders'], music_path,
            'assets/models/tracks/%s/collision' % track_path,
            ['Road', 'Offroad'], ['Wall'],
            ['Goal', 'Slow', 'Respawn', 'PitStop'], corner_names,
            ['Waypoints', 'Waypoint', 'prev'],
            self.mdt.options['development']['show_waypoints'],
            self.mdt.options['development']['weapons'],
            ['Weaponboxs', 'EmptyWeaponboxAnim'], 'Start', track_path,
            'tracks/' + track_path, 'track', 'Empty', 'Anim', 'omni',
            sign_cb, 'EmptyNameBillboard4Anim',
            'assets/images/minimaps/%s.png' % track_path,
            'assets/images/minimaps/car_handle.png', col_dct, camera_vec,
            shadow_src, laps, 'assets/models/weapons/rocket/rocket',
            'assets/models/weapons/bonus/WeaponboxAnim', 'Anim',
            ['kronos', 'themis', 'diones', 'iapeto'],
            self.mdt.options['development']['ai'], InGameMenu,
            Utils().menu_args, 'assets/images/drivers/driver%s_sel.png',
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
        return race_props
