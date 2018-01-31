from collections import namedtuple
from yaml import load
from direct.gui.OnscreenText import OnscreenText
from yyagl.game import GameLogic
from yyagl.racing.season.season import SingleRaceSeason, Season, SeasonProps
from yyagl.racing.driver.driver import Driver, DriverProps, DriverInfo
from yyagl.racing.race.raceprops import RaceProps
from menu.ingamemenu.menu import InGameMenu
from .thanksnames import ThanksNames
from menu.multiplayer.multiplayerfrm import MultiplayerFrm


class YorgLogic(GameLogic):

    def __init__(self, mediator):
        GameLogic.__init__(self, mediator)
        self.season = self.mp_frm = None
        self.eng.do_later(.01, self.init_mp_frm)

    def init_mp_frm(self):
        if not self.mp_frm:
            self.mp_frm = MultiplayerFrm(self.mediator.gameprops.menu_args)
            self.mp_frm.attach(self.on_msg_focus)
            self.mp_frm.attach(self.on_create_room)

    def on_start(self):
        GameLogic.on_start(self)

        self.__process_default()
        dev = self.mediator.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        if car and track:  # for development's quickstart
            self.season = SingleRaceSeason(self.__season_props(
                self.mediator.gameprops, car, [],
                self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
                dev['race_start_time'], dev['countdown_seconds']))
            self.season.attach_obs(self.mediator.event.on_season_end)
            self.season.attach_obs(self.mediator.event.on_season_cont)
            self.season.start()
            self.mediator.fsm.demand('Race', track, car, [car],
                                self.season.logic.drivers, self.season.ranking)
        else:
            self.mediator.fsm.demand('Menu')

    @staticmethod
    def __season_props(
            gameprops, car, player_car_names, cars_number, single_race,
            tun_engine, tun_tires, tun_suspensions, race_start_time,
            countdown_seconds):
        wpn2img = {
            'Rocket': 'rocketfront',
            'RearRocket': 'rocketrear',
            'Turbo': 'turbo',
            'RotateAll': 'turn',
            'Mine': 'mine'}
        drivers = []
        for drv_info, car_name in zip(gameprops.drivers_info,
                                      gameprops.cars_names):
            drivers += [Driver(DriverProps(drv_info, car_name, 0, 0, 0))]
        if car not in gameprops.cars_names[:int(cars_number)]:
            cars = gameprops.cars_names[:int(cars_number) - 1] + [car]
        else:
            cars = gameprops.cars_names[:int(cars_number)]
        return SeasonProps(
            gameprops, cars, car, player_car_names, drivers,
            ['assets/images/tuning/engine.txo',
             'assets/images/tuning/tires.txo',
             'assets/images/tuning/suspensions.txo'],
            'assets/fonts/Hanken-Book.ttf',
            'assets/sfx/countdown.ogg', single_race, wpn2img, tun_engine,
            tun_tires, tun_suspensions, race_start_time, countdown_seconds)

    def __process_default(self):
        opt_ver = self.mediator.options['settings']['last_version'].split('-')[0]
        curr_ver = self.eng.version.split('-')[0]
        if curr_ver == '0.8.0' and opt_ver == '0.7.0':
            if self.mediator.options['settings']['cars_number'] == 7:
                self.mediator.options['settings']['cars_number'] = 8
        self.mediator.options['settings']['last_version'] = self.eng.version
        self.mediator.options.store()

    def on_msg_focus(self, val):
        self.mediator.fsm.enable_menu(val == 'out')

    def on_create_room(self, room, nick):
        self.mediator.fsm.create_room(room, nick)

    def on_input_back(self, new_opt_dct):
        self.mediator.options['settings'].update(new_opt_dct)
        self.mediator.options.store()

    def on_options_back(self, new_opt_dct):
        self.mediator.options['settings'].update(new_opt_dct)
        self.mediator.options.store()
        # refactor: now the page props are static, but they should change
        # when we change the options in the option page

    def on_car_selected(self, car):
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops, car, [car],
            self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_car_start_client(self, track, car, cars, packet):
        drv_info = self.mediator.gameprops.drivers_info
        for i, drv_name in enumerate(packet[4::3]):
            drv_info[i] = drv_info[i]._replace(name=drv_name)
        self.mediator.gameprops = self.mediator.gameprops._replace(drivers_info=drv_info)
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops, car, cars,
            self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()
        self.mediator.fsm.demand('Race', track, car, cars,
                            self.season.logic.drivers)

    def on_car_selected_season(self, car):
        dev = self.mediator.options['development']
        self.season = Season(self.__season_props(
            self.mediator.gameprops, car, [car],
            self.mediator.options['settings']['cars_number'], False, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_driver_selected(self, player_name, track, car):
        self.mediator.options['settings']['player_name'] = player_name
        self.mediator.gameprops = self.mediator.gameprops._replace(
            player_name=player_name)
        self.mediator.options.store()
        for i, drv in enumerate(self.season.logic.drivers):
            dinfo = self.mediator.gameprops.drivers_info[i]
            drv.logic.dprops = drv.logic.dprops._replace(info=dinfo)
        self.eng.do_later(
            2.0, self.mediator.fsm.demand,
            ['Race', track, car, [car], self.season.logic.drivers])

    def on_driver_selected_server(self, player_name, track, car, cars, packet):
        # unused packet
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops, car, cars,
            self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()
        self.mediator.options['settings']['player_name'] = player_name
        self.mediator.gameprops = self.mediator.gameprops._replace(
            player_name=player_name)
        self.mediator.options.store()
        for i, drv in enumerate(self.season.logic.drivers):
            dinfo = self.mediator.gameprops.drivers_info[i]
            drv.logic.dprops = drv.logic.dprops._replace(info=dinfo)
        self.eng.do_later(
            2.0, self.mediator.fsm.demand,
            ['Race', track, car, cars, self.season.logic.drivers])

    def on_continue(self):
        saved_car = self.mediator.options['save']['car']
        dev = self.mediator.options['development']
        tuning = self.mediator.options['save']['tuning']
        car_tun = tuning[saved_car]
        drivers = [self.__bld_drv(dct)
                   for dct in self.mediator.options['save']['drivers']]
        self.season = Season(self.__season_props(
            self.mediator.gameprops, saved_car, [saved_car],
            self.mediator.options['settings']['cars_number'], False,
            car_tun.f_engine, car_tun.f_tires, car_tun.f_suspensions,
            dev['race_start_time'], dev['countdown_seconds']))
        self.season.load(self.mediator.options['save']['ranking'],
                         tuning, drivers)
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start(False)
        track_path = self.mediator.options['save']['track']
        car_path = self.mediator.options['save']['car']
        self.mediator.fsm.demand('Race', track_path, car_path, [car_path], drivers)

    @staticmethod
    def __bld_drv(dct):
        drv = Driver(
            DriverProps(
                DriverInfo(dct['img_idx'], dct['name'], dct['speed'],
                dct['adherence'], dct['stability']), dct['car_name'],
                dct['f_engine'], dct['f_tires'], dct['f_suspensions']))
        return drv

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
            self.mediator.options['save']['ranking'] = ranking.carname2points
            self.mediator.options['save']['tuning'] = tuning.car2tuning
            self.mediator.options.store()
            self.mediator.fsm.demand('Ranking')
        else:
            self.season.logic.notify('on_season_end', True)

    def on_login(self):
        self.init_mp_frm()
        self.eng.xmpp.send_connected()
        self.mp_frm.on_users()

    def on_logout(self):
        self.mp_frm.on_users()

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

    def build_race_props(self, drivers, track_name, keys, joystick,
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
        share_urls = [
            'https://www.facebook.com/sharer/sharer.php?u=' +
            'ya2.it/pages/yorg.html',
            'https://twitter.com/share?text=I%27ve%20achieved%20{time}'
            '%20in%20the%20{track}%20track%20on%20Yorg%20by%20%40ya2tech'
            '%21&hashtags=yorg',
            'https://plus.google.com/share?url=ya2.it/pages/yorg.html',
            'https://www.tumblr.com/widgets/share/tool?url=ya2.it']
        items = self.season.ranking.carname2points.items()
        grid_rev_ranking = sorted(items, key=lambda el: el[1])
        grid = [pair[0] for pair in grid_rev_ranking]
        race_props = RaceProps(
            self.season.props, keys, joystick, sounds,
            'assets/models/cars/%s/capsule', 'Capsule', 'assets/models/cars',
            wheel_names, 'Road',
            'assets/particles/sparks.ptf', drivers,
            self.mediator.options['development']['shaders_dev'],
            self.mediator.options['settings']['shaders'], music_fpath,
            'assets/models/tracks/%s/collision' % track_name,
            ['Road', 'Offroad'], ['Wall'],
            ['Goal', 'Slow', 'Respawn', 'PitStop'], corner_names,
            WPInfo('Waypoints', 'Waypoint', 'prev'),
            self.mediator.options['development']['show_waypoints'],
            WeaponInfo('Weaponboxs', 'EmptyWeaponboxAnim'), 'Start',
            track_name, 'tracks/' + track_name, 'track', 'Empty', 'Anim',
            'omni', self.sign_cb, 'EmptyNameBillboard4Anim',
            'assets/images/minimaps/%s.txo' % track_name,
            'assets/images/minimaps/car_handle.txo', carname2color, camera_vec,
            shadow_src, laps_num, 'assets/models/weapons/rocket/RocketAnim',
            'assets/models/weapons/turbo/TurboAnim',
            'assets/models/weapons/turn/TurnAnim',
            'assets/models/weapons/mine/MineAnim',
            'assets/models/weapons/bonus/WeaponboxAnim', 'Anim',
            self.mediator.options['development']['ai'], InGameMenu, share_urls,
            'Respawn', 'PitStop', 'Wall', 'Goal', 'Bonus', ['Road', 'Offroad'],
            grid)
        return race_props
