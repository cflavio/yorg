from collections import namedtuple
from yaml import load
from direct.gui.OnscreenText import OnscreenText
from yyagl.game import GameLogic
from yyagl.racing.season.season import SingleRaceSeason, Season, SeasonProps
from yyagl.racing.driver.driver import Driver, DriverProps
from yyagl.racing.race.raceprops import RaceProps
from menu.ingamemenu.menu import InGameMenu
from .thanksnames import ThanksNames


class YorgLogic(GameLogic):

    def __init__(self, mdt):
        GameLogic.__init__(self, mdt)
        self.season = self.curr_cars = None

    def on_start(self):
        GameLogic.on_start(self)
        self.__process_default()
        dev = self.mdt.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        if car and track:  # for development's quickstart
            self.season = SingleRaceSeason(self.__season_props(
                self.mdt.gameprops, car,
                self.mdt.options['settings']['cars_number'], True, 0, 0, 0,
                dev['race_start_time'], dev['countdown_seconds']))
            self.season.attach_obs(self.mdt.event.on_season_end)
            self.season.attach_obs(self.mdt.event.on_season_cont)
            self.season.start()
            #for drv, car_name in zip(self.season.logic.drivers, self.mdt.gameprops.cars_names):
            #    drv.dprops = drv.dprops._replace(car_name=car_name)
            self.mdt.fsm.demand('Race', track, car, self.season.logic.drivers)
        else:
            self.mdt.fsm.demand('Menu')

    def __season_props(
            self, gameprops, car, cars_number, single_race, tun_engine,
            tun_tires, tun_suspensions, race_start_time, countdown_seconds):
        wpn2img = {
            'Rocket': 'rocketfront',
            'RearRocket': 'rocketrear',
            'Turbo': 'turbo',
            'RotateAll': 'turn',
            'Mine': 'mine'}
        drivers = []
        for drv_info, car_name in zip(gameprops.drivers_info, gameprops.cars_names):
            drivers += [Driver(DriverProps(drv_info, car_name, 0, 0, 0))]
        return SeasonProps(
            gameprops, gameprops.cars_names[:int(cars_number)], car, drivers,
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            'assets/fonts/Hanken-Book.ttf',
            'assets/sfx/countdown.ogg', single_race, wpn2img, tun_engine,
            tun_tires, tun_suspensions, race_start_time, countdown_seconds)

    def __process_default(self):
        opt_ver = self.mdt.options['settings']['last_version'].split('-')[0]
        curr_ver = self.eng.version.split('-')[0]
        if curr_ver == '0.8.0' and opt_ver == '0.7.0':
            if self.mdt.options['settings']['cars_number'] == 7:
                self.mdt.options['settings']['cars_number'] = 8
        self.mdt.options['settings']['last_version'] = self.eng.version
        self.mdt.options.store()

    def on_input_back(self, new_opt_dct):
        self.mdt.options['settings'].update(new_opt_dct)
        self.mdt.options.store()

    def on_options_back(self, new_opt_dct):
        self.mdt.options['settings'].update(new_opt_dct)
        self.mdt.options.store()
        cars_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                      'iperion', 'teia']
        self.curr_cars = cars_names[:int(new_opt_dct['cars_number'])]  # put it there
        # refactor: now the page props are static, but they should change
        # when we change the options in the option page

    def on_car_selected(self, car):
        dev = self.mdt.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mdt.gameprops, car,
            self.mdt.options['settings']['cars_number'], True, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)
        self.season.start()

    def on_car_selected_season(self, car):
        dev = self.mdt.options['development']
        self.season = Season(self.__season_props(
            self.mdt.gameprops, car,
            self.mdt.options['settings']['cars_number'], False, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)
        self.season.start()

    def on_driver_selected(self, player_name, track, car):
        self.mdt.options['settings']['player_name'] = player_name
        self.mdt.options.store()
        #new_gp = self.season.props.gameprops._replace(drivers_skills=drivers_skills)
        #self.season.logic.props = self.season.logic.props._replace(gameprops=new_gp)
        for drv, car_name in zip(self.season.logic.drivers, self.mdt.gameprops.cars_names):
            drv.logic.dprops = drv.dprops._replace(car_name=car_name)
            if car_name == car:
                info = drv.logic.dprops.info._replace(name=player_name)
                drv.logic.dprops = drv.logic.dprops._replace(info=info)
        self.eng.do_later(2.0, self.mdt.fsm.demand, ['Race', track, car, self.season.logic.drivers])

    def on_continue(self):
        saved_car = self.mdt.options['save']['car']
        dev = self.mdt.options['development']
        tuning = self.mdt.options['save']['tuning']
        car_tun = tuning[saved_car]
        self.season = Season(self.__season_props(
            self.mdt.gameprops, saved_car,
            self.mdt.options['settings']['cars_number'], False,
            car_tun.f_engine, car_tun.f_tires, car_tun.f_suspensions,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.load(self.mdt.options['save']['ranking'],
                         tuning, self.mdt.options['save']['drivers'])
        self.season.attach_obs(self.mdt.event.on_season_end)
        self.season.attach_obs(self.mdt.event.on_season_cont)
        self.season.start(False)
        track_path = self.mdt.options['save']['track']
        car_path = self.mdt.options['save']['car']
        drivers = self.mdt.options['save']['drivers']
        self.mdt.fsm.demand('Race', track_path, car_path, drivers)

    def on_race_loaded(self):
        self.season.race.event.detach(self.on_race_loaded)
        self.season.race.results.attach(self.on_race_step)

    def on_race_step(self, race_ranking):
        self.season.race.results.detach(self.on_race_step)
        ranking = self.season.ranking
        tuning = self.season.tuning
        if self.season.__class__ != SingleRaceSeason:
            for car in ranking.carname2points:
                ranking.carname2points[car] += race_ranking[car]
            self.mdt.options['save']['ranking'] = ranking.carname2points
            self.mdt.options['save']['tuning'] = tuning.car2tuning
            self.mdt.options.store()
            self.mdt.fsm.demand('Ranking')
        else:
            self.season.logic.notify('on_season_end', True)

    @staticmethod
    def sign_cb(parent):
        text = '\n\n'.join(ThanksNames.get_thanks(3, 4))
        txt = OnscreenText(text, parent=parent, scale=.2, fg=(0, 0, 0, 1),
                           pos=(.245, 0))
        bounds = lambda: txt.get_tight_bounds()
        while bounds()[1].x - bounds()[0].x > .48:
            scale = txt.getScale()[0]
            # NB getScale is OnscreenText's meth; it doesn't have swizzle
            txt.setScale(scale - .01, scale - .01)
        bounds = txt.get_tight_bounds()
        height = bounds[1].z - bounds[0].z
        txt.set_z(.06 + height / 2)

    def build_race_props(self, car_path, drivers, track_name, keys, joystick,
                         sounds):
        Wheels = namedtuple('Wheels', 'fr fl rr rl')
        frwheels = Wheels('EmptyWheelFront', 'EmptyWheelFront.001',
                          'EmptyWheelRear', 'EmptyWheelRear.001')
        # names for front and rear wheels
        bwheels = Wheels('EmptyWheel', 'EmptyWheel.001', 'EmptyWheel.002',
                         'EmptyWheel.003')
        # names for both wheels
        WheelNames = namedtuple('WheelNames', 'frontrear both')
        wheel_names = WheelNames(frwheels, bwheels)
        wheel_gfx_names = ['wheelfront', 'wheelrear', 'wheel']
        wheel_gfx_names = [self.eng.curr_path + 'assets/models/cars/%s/' + wname
                           for wname in wheel_gfx_names]
        WheelGfxNames = namedtuple('WheelGfxNames', 'front rear both')
        wheel_gfx_names = WheelGfxNames(*wheel_gfx_names)

        track_fpath = 'assets/models/tracks/%s/track.yml' % track_name
        with open(self.eng.curr_path + track_fpath) as ftrack:
            music_name = load(ftrack)['music']
        music_fpath = 'assets/music/%s.ogg' % music_name
        corner_names = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corner_names = ['Minimap' + crn for crn in corner_names]
        carname2color = {'kronos': (0, 0, 1, 1), 'themis': (1, 0, 0, 1),
                         'diones': (1, 1, 1, 1), 'iapeto': (1, 1, 0, 1),
                         'phoibe': (.6, .6, 1, 1), 'rea': (0, 0, .6, 1),
                         'iperion': (.8, .8, .8, 1), 'teia': (0, 0, 0, 1)}
        with open(self.eng.curr_path + track_fpath) as ftrack:
            track_cfg = load(ftrack)
            camera_vec = track_cfg['camera_vector']
            shadow_src = track_cfg['shadow_source']
            laps_num = track_cfg['laps']
        WPInfo = namedtuple('WPInfo', 'root_name wp_name prev_name')
        WeaponInfo = namedtuple('WeaponInfo', 'root_name weap_name')
        DamageInfo = namedtuple('DamageInfo', 'low hi')
        damage_info = DamageInfo('assets/models/cars/%s/cardamage1',
                                 'assets/models/cars/%s/cardamage2')
        car_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                     'iperion', 'teia']
        share_urls = [
            'https://www.facebook.com/sharer/sharer.php?u=ya2.it/yorg',
            'https://twitter.com/share?text=I%27ve%20achieved%20{time}'
            '%20in%20the%20{track}%20track%20on%20Yorg%20by%20%40ya2tech'
            '%21&hashtags=yorg',
            'https://plus.google.com/share?url=ya2.it/yorg',
            'https://www.tumblr.com/widgets/share/tool?url=ya2.it']
        items = game.logic.season.ranking.carname2points.items()
        grid_rev_ranking = sorted(items, key=lambda el: el[1])
        grid = [pair[0] for pair in grid_rev_ranking]
        race_props = RaceProps(
            self.season.props, keys, joystick, sounds,
            'assets/models/cars/%s/capsule', 'Capsule', 'assets/models/cars',
            wheel_names, 'Road', 'assets/models/cars/%s/car',
            damage_info, wheel_gfx_names,
            'assets/particles/sparks.ptf', drivers,
            self.mdt.options['development']['shaders_dev'],
            self.mdt.options['settings']['shaders'], music_fpath,
            'assets/models/tracks/%s/collision' % track_name,
            ['Road', 'Offroad'], ['Wall'],
            ['Goal', 'Slow', 'Respawn', 'PitStop'], corner_names,
            WPInfo('Waypoints', 'Waypoint', 'prev'),
            self.mdt.options['development']['show_waypoints'],
            WeaponInfo('Weaponboxs', 'EmptyWeaponboxAnim'), 'Start',
            track_name, 'tracks/' + track_name, 'track', 'Empty', 'Anim',
            'omni', self.sign_cb, 'EmptyNameBillboard4Anim',
            'assets/images/minimaps/%s.png' % track_name,
            'assets/images/minimaps/car_handle.png', carname2color, camera_vec,
            shadow_src, laps_num, 'assets/models/weapons/rocket/RocketAnim',
            'assets/models/weapons/turbo/TurboAnim',
            'assets/models/weapons/turn/TurnAnim',
            'assets/models/weapons/mine/MineAnim',
            'assets/models/weapons/bonus/WeaponboxAnim', 'Anim',
            self.mdt.options['development']['ai'], InGameMenu, share_urls,
            'Respawn', 'PitStop', 'Wall', 'Goal', 'Bonus', ['Road', 'Offroad'], grid)
        return race_props
