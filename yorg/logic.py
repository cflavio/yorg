from logging import info
from random import shuffle
from os import walk
from json import load
from direct.gui.OnscreenText import OnscreenText
from yyagl.game import GameLogic
from yyagl.dictfile import DctFile
from yracing.season.season import SingleRaceSeason, Season, SeasonProps
from yracing.player.player import Player, TuningPlayer
from yracing.driver.driver import Driver
from yracing.race.raceprops import RaceProps
from menu.ingamemenu.menu import InGameMenu
from menu.netmsgs import NetMsgs
from .thanksnames import ThanksNames


class Wheels:

    def __init__(self, front_right, front_left, rear_right, rear_left):
        self.fr = front_right
        self.fl = front_left
        self.rr = rear_right
        self.rl = rear_left


class WheelNames:

    def __init__(self, frontrear, both):
        self.frontrear = frontrear
        self.both = both


class WPInfo:

    def __init__(self, root_name, wp_name, prev_name):
        self.root_name = root_name
        self.wp_name = wp_name
        self.prev_name = prev_name


class WeaponInfo:

    def __init__(self, root_name, weap_name):
        self.root_name = root_name
        self.weap_name = weap_name


class YorgLogic(GameLogic):

    def __init__(self, mediator):
        GameLogic.__init__(self, mediator)
        self.season = None  # self.mp_frm = None
        # self.eng.do_later(.01, self.init_mp_frm)
        dev = self.mediator.options['development']
        cars = dev['cars'] if 'cars' in dev else ''
        # track = dev['track'] if 'track' in dev else ''
        server = dev['server'] if 'server' in dev else ''
        self.sel_track = None
        self.current_drivers = None
        if cars and server:  # for development's quickstart
            self.mediator.options.persistent = False

    def init_mp_frm(self):
        dev = self.mediator.options['development']
        cars = dev['cars'] if 'cars' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        server = dev['server'] if 'server' in dev else ''
        # if not self.mp_frm and not (cars and track and not server):
        if not (cars and track and not server):
            # self.mp_frm = MultiplayerFrm(self.mediator.gameprops.menu_props,
            #                              self.eng.cfg.dev_cfg.xmpp_server)
            # self.mp_frm.attach(self.on_msg_focus)
            # self.mp_frm.attach(self.on_srv_quitted)
            # self.mp_frm.attach(self.on_removed)
            # self.mp_frm.attach(self.on_start_match)
            # self.mp_frm.attach(self.on_start_match_client)
            if not (cars and track):
                self.mediator.fsm.menu.logic.attach(self.on_start_match)
                self.mediator.fsm.menu.logic.attach(
                    self.on_start_match_client_menu)

    def on_start(self):
        GameLogic.on_start(self)
        self.__process_default()
        dev = self.mediator.options['development']
        cars = dev['cars'] if 'cars' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        server = dev['server'] if 'server' in dev else ''
        if cars and track and not dev['mp_srv_usr']:
            # for development's quickstart
            cars = cars.split()
            cars0 = cars
            if len(cars) == 1: cars0 = cars[0]
            self.season = SingleRaceSeason(YorgLogic.__season_props(
                self.mediator.gameprops,
                self.mediator.options['settings']['cars_number'], True,
                dev['race_start_time'], dev['countdown_seconds'],
                self.mediator.options['settings']['camera'], 'single'))
            self.season.attach_obs(self.mediator.event.on_season_end)
            self.season.attach_obs(self.mediator.event.on_season_cont)
            self.season.logic.players += [Player(
                car=cars0, driver=Driver(0, 'quickstart', 0, 0, 0),
                kind=Player.human, tuning=TuningPlayer(0, 0, 0))]
            self.season.start()
            self.mediator.fsm.demand('Race', track, self.season.logic.players,
                                     self.season.ranking)
            # taskMgr.doMethodLater(
            #     5.0, lambda task: self.mediator.logic.mp_frm.hide(), 'hide')
        elif cars and server:  # for development's quickstart
            self.season = SingleRaceSeason(YorgLogic.__season_props(
                self.mediator.gameprops,
                self.mediator.options['settings']['cars_number'], True,
                dev['race_start_time'], dev['countdown_seconds'],
                self.mediator.options['settings']['camera'], 'onlinemp'))
            self.season.attach_obs(self.mediator.event.on_season_end)
            self.season.attach_obs(self.mediator.event.on_season_cont)
            self.season.start()
            if server == 'server':  # i am the server
                def process_msg(data_lst, sender):
                    if data_lst[0] == NetMsgs.car_request:
                        client_car = data_lst[1]
                        self.eng.car_mapping[data_lst[-1]] = client_car
                        info('car requested: %s %s' % (
                            data_lst[-1], client_car))
                    if data_lst[0] == NetMsgs.driver_selection:
                        s_ip = sender.get_address().get_ip_string()
                        if s_ip not in self.current_drivers:
                            self.current_drivers += [s_ip]
                        _car = data_lst[1]
                        driver_name = data_lst[2]
                        driver_id = data_lst[3]
                        driver_speed = data_lst[4]
                        driver_adherence = data_lst[5]
                        driver_stability = data_lst[6]
                        info('driver selected: %s (%s, %s) ' % (
                            driver_name, driver_id, _car))
                        # gprops = self.mediator.gameprops
                        # cars = gprops.cars_names[:]
                        # car_idx = cars.index(_car)
                        # gprops.drivers_info[car_idx] = \
                        #     gprops.drivers_info[car_idx]._replace(
                        #         img_idx=driver_id)
                        # gprops.drivers_info[car_idx] = \
                        #     gprops.drivers_info[car_idx]._replace(
                        #         name=driver_name)
                        # gprops.drivers_info[car_idx] = \
                        #     gprops.drivers_info[car_idx]._replace(
                        #         speed=driver_speed)
                        # gprops.drivers_info[car_idx] = \
                        #     gprops.drivers_info[car_idx]._replace(
                        #         adherence=driver_adherence)
                        # gprops.drivers_info[car_idx] = \
                        #     gprops.drivers_info[car_idx]._replace(
                        #         stability=driver_stability)
                        sprops = self.season.props
                        drivers = sprops.drivers
                        for drv in drivers:
                            if drv.dprops.info.img_idx == driver_id:
                                drv.logic.dprops.car_name = _car
                                drv.logic.dprops.info.name = driver_name
                                drv.logic.dprops.info.speed = driver_speed
                                drv.logic.dprops.info.adherence = \
                                    driver_adherence
                                drv.logic.dprops.info.stability = \
                                    driver_stability
                        sprops.drivers = drivers
                        self.start_network_race_server(cars, track)

                def process_connection(client_address):
                    info('connection from ' + client_address)
                    self.current_drivers = [self, client_address]
                self.eng.server.start(process_msg, process_connection)
                self.eng.car_mapping = {}
                self.eng.car_mapping['self'] = cars
                # gprops = self.mediator.gameprops
                # cars = gprops.cars_names[:]
                # car_idx = cars.index(car)
                # cars.remove(car)
                # shuffle(cars)
                # drv_idx = range(8)
                # drv_idx.remove(0)
                # shuffle(drv_idx)
                # gprops.drivers_info[car_idx] = \
                #     gprops.drivers_info[0]._replace(
                #         img_idx=0)
                # nname = self.mediator.options['settings']['player_name']
                # gprops.drivers_info[car_idx] = \
                #     gprops.drivers_info[0]._replace(
                #         name=nname)
                # gprops.drivers_info[0] = gprops.drivers_info[0]._replace(
                #     img_idx=car_idx)
                sprops = self.season.props
                drivers = sprops.drivers
                for i, drv in enumerate(drivers):
                    if drv.dprops.info.img_idx == 0:
                        drv.logic.dprops.car_name = None
                        # car - car is undefined
                        drv.logic.dprops.info.name = \
                            self.mediator.options['settings'][
                                'player_names'][i]
            else:
                def process_msg(data_lst, sender):  # unused sender
                    if data_lst[0] == NetMsgs.track_selected:
                        info('track selected (yorg.logic): ' + data_lst[1])
                        self.sel_track = data_lst[1]
                    if data_lst[0] == NetMsgs.start_race:
                        info('start_race: ' + str(data_lst))
                        # cars = data_lst[4::7]
                        # self.on_car_start_client(
                        #     self.sel_track, car, cars, data_lst, None)
                        # TODO room is None
                        # TODO car is undefined
                self.eng.client.start(process_msg)
                # self.eng.client.send([NetMsgs.car_request, car,
                #                      self.eng.client.my_addr])
                # car is undefined
                # gprops = self.mediator.gameprops
                sprops = self.season.props
                drivers = sprops.drivers
                for drv in drivers:
                    if drv.dprops.info.img_idx == 1:
                        curr_drv = drv  # unused curr_drv
                # self.eng.client.send([
                #     NetMsgs.driver_selection, car,
                #     self.mediator.options['settings']['player_name'], 1,
                #     gprops.drivers_info[1].speed,
                #     gprops.drivers_info[1].adherence,
                #     gprops.drivers_info[1].stability,
                #     self.eng.client.my_addr])
                # self.eng.client.send([
                #     NetMsgs.driver_selection, car,
                #     self.mediator.options['settings']['player_names'][0], 1,
                #     curr_drv.dprops.info.speed,
                #     curr_drv.dprops.info.adherence,
                #     curr_drv.dprops.info.stability,
                #     self.eng.client.my_addr])
                # car is undefined
        else:
            self.mediator.fsm.demand('Menu')

    def on_start_match(self):
        self.mediator.fsm.on_start_match()

    def on_start_match_client_menu(self, track):
        self.mediator.fsm.on_start_match_client(track)

    def start_network_race_server(self, car, track):
        self.eng.server.send([NetMsgs.track_selected, track])
        packet = [NetMsgs.start_race, len(self.current_drivers)]

        def process(k):
            '''Processes a car.'''
            return 'server' if k == self else str(k)
        # gprops = self.mediator.gameprops
        # for i, k in enumerate(self.current_drivers):
        #     car_idx = gprops.drivers_info[i].img_idx
        #     packet += [process(k), gprops.cars_names[car_idx],
        #                self.mediator.gameprops.drivers_info[i].name]
        cars_names = []
        sprops = self.season.props
        drivers = sprops.drivers
        for i, k in enumerate(self.current_drivers):
            drv = drivers[i]
            packet += [process(k), drv.dprops.info.img_idx,
                       drv.dprops.car_name, drv.dprops.info.name,
                       drv.dprops.info.speed, drv.dprops.info.adherence,
                       drv.dprops.info.stability]
            cars_names += [drv.dprops.car_name]
        # self.eng.server.send(packet)
        # self.eng.log_mgr.log('start race (server): ' + str(packet))
        info('drivers: ' + str(drivers))
        info('current drivers: ' + str(self.current_drivers))
        self.on_driver_selected_server(
            self.mediator.options['settings']['player_names'][0], track, car,
            cars_names)

    @staticmethod
    def __season_props(
            gameprops, cars_number, single_race, race_start_time,
            countdown_seconds, camera, kind, room=None):
        wpn2img = {
            'Rocket': 'rocketfront',
            'RearRocket': 'rocketrear',
            'Turbo': 'turbo',
            'RotateAll': 'turn',
            'Mine': 'mine'}
        # drivers = []
        # for drv_info in gameprops.drivers_info:
        #     drivers += [Driver(DriverProps(drv_info, None, 0, 0, 0))]
        # player_car_names = [player.car for player in players
        #                     if player.kind == Player.human]
        # cars_number = len(player_car_names)
        # cars = player_car_names[:] + gameprops.cars_names
        # cars = list(OrderedDict.fromkeys(cars))[:int(cars_number)]
        # cars = list(dict.fromkeys(cars))[:int(cars_number)]  # python 3.6
        return SeasonProps(
            gameprops, cars_number,
            ['assets/images/tuning/engine.txo',
             'assets/images/tuning/tires.txo',
             'assets/images/tuning/suspensions.txo'],
            'assets/fonts/Hanken-Book.ttf',
            'assets/sfx/countdown.ogg', single_race, wpn2img, race_start_time,
            countdown_seconds, camera, kind, room)

    def __process_default(self):
        opt_ver = self.mediator.options['settings'][
            'last_version'].split('-')[0]
        curr_ver = self.eng.version.split('-')[0]
        if curr_ver == '0.8.0' and opt_ver == '0.7.0':
            if self.mediator.options['settings']['cars_number'] == 7:
                self.mediator.options['settings']['cars_number'] = 8
        if curr_ver == '0.11.0' and opt_ver == '0.10.0':
            self.mediator.options['development']['multithreaded_render'] = 1
        self.mediator.options['settings']['last_version'] = self.eng.version
        self.mediator.options.store()

    def on_msg_focus(self, val):
        self.mediator.fsm.enable_menu_navigation(val == 'out')

    def on_srv_quitted(self):
        # self.eng.client.stop()
        self.mediator.fsm.on_srv_quitted()

    def on_removed(self):
        self.mediator.fsm.on_removed()

    def on_input_back(self, new_opt_dct):
        self.mediator.options['settings'] = DctFile.deepupdate(
            self.mediator.options['settings'], new_opt_dct)
        self.mediator.options.store()

    def on_options_back(self, new_opt_dct):
        self.mediator.options['settings'].update(new_opt_dct)
        self.mediator.options.store()
        # refactor: now the page props are static, but they should change
        # when we change the options in the option page

    def on_room_back(self):
        if self.eng.server.is_active: self.eng.server.stop()
        # if self.eng.client.is_active: self.eng.client.stop()
        # self.mp_frm.on_room_back()

    def on_quit(self):
        pass  # self.mp_frm.on_quit()

    def on_single_race(self):
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], True,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'single'))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_start_season(self):
        dev = self.mediator.options['development']
        self.season = Season(self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], False,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'season'))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_start_local_mp(self):
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], True,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'localmp'))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_start_mp_server(self):
        dev = self.mediator.options['development']
        # self.season = SingleRaceSeason(self.__season_props(
        #     self.mediator.gameprops, car, cars,
        #     self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
        #     dev['race_start_time'], dev['countdown_seconds']))
        sprops = self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], True,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'onlinemp')
        # sprops.car_names = cars
        # sprops.player_car_names = cars
        self.season = SingleRaceSeason(sprops)
        # for i, drv in enumerate(self.season.logic.drivers):
        #     dinfo = self.mediator.gameprops.drivers_info[i]
        #     drv.logic.dprops.info = dinfo
        # self.season.logic.props.car_names = cars
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_start_mp_client(self):
        dev = self.mediator.options['development']
        self.season = SingleRaceSeason(self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], True,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'localmp'))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start()

    def on_car_selected(self, car):
        self.season.logic.players += [Player(
            car=car, kind=Player.human, tuning=TuningPlayer(0, 0, 0))]
        self.mediator.fsm.menu.logic.players = self.season.logic.players

    def on_track_selected(self):
        self.mediator.fsm.menu.logic.players_omp = self.season.logic.players

    def on_track_selected_mp(self):
        self.mediator.fsm.menu.logic.players_mp = self.season.logic.players

    def on_car_selected_mp(self, car, player_idx):
        self.season.logic.players += [Player(
            car=car, kind=Player.human, tuning=TuningPlayer(0, 0, 0),
            human_idx=player_idx)]

    def on_car_selected_omp_srv(self, car):
        self.season.logic.players = [Player(
            car=car, kind=Player.human, tuning=TuningPlayer(0, 0, 0),
            human_idx=0)]

    def on_car_selected_omp_client(self, car):
        self.season.logic.players = [Player(
            car=car, kind=Player.human, tuning=TuningPlayer(0, 0, 0),
            human_idx=0)]

    def on_car_start_client(self, track, car, cars, packet, room):
        # unused car, cars, room
        # drv_info = self.mediator.gameprops.drivers_info
        # for i, drv_name in enumerate(packet[4::3]):
        #     drv_info[i] = drv_info[i]._replace(name=drv_name)
        # self.mediator.gameprops = self.mediator.gameprops._replace(
        #     drivers_info=drv_info)
        # dev = self.mediator.options['development']
        # #sprops = self.__season_props(
        #     self.mediator.gameprops, True,
        #     dev['race_start_time'], dev['countdown_seconds'],
        #     self.mediator.options['settings']['camera'], 'onlinemp', room)
        # self.season = SingleRaceSeason(sprops)
        # drivers = self.season.logic.drivers
        packet_drivers = []
        for i in range(packet[0]):
            offset = i * 6
            pdrv = packet[1 + offset: 1 + offset + 6]
            packet_drivers += [pdrv]
        this_human_car = self.season.logic.players[0].car
        self.season.logic.players = []
        for pdrv in packet_drivers:
            driver = Driver(img_idx=pdrv[0], name=pdrv[1], speed=pdrv[3],
                            adherence=pdrv[4], stability=pdrv[5])
            is_player = pdrv[1] == this_human_car
            player = Player(
                driver=driver, car=pdrv[1],
                kind=Player.human if is_player else Player.network,
                tuning=TuningPlayer(0, 0, 0),
                human_idx=0 if is_player else None, name=pdrv[2])
            self.season.logic.players += [player]
        # for i, pdrv in enumerate(packet_drivers):
        #     prev_drv = drivers[i]
        #     for j, drv in enumerate(drivers):
        #         if drv.dprops.info.img_idx == pdrv[0]:
        #             drivers[i] = drv
        #             drivers[j] = prev_drv
        # sprops.drivers = drivers
        # sprops.car_names = cars

        # self.season = SingleRaceSeason(self.__season_props(
        #     self.mediator.gameprops, car, cars,
        #     self.mediator.options['settings']['cars_number'], True, 0, 0, 0,
        #     dev['race_start_time'], dev['countdown_seconds']))
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        # self.season.start()
        self.mediator.fsm.demand('Race', track, self.season.logic.players)

    def on_car_selected_season(self, car):
        self.season.logic.players += [Player(
            car=car, kind=Player.human, tuning=TuningPlayer(0, 0, 0))]

    def on_driver_selected(self, player_name, track, car, i):
        self.mediator.options['settings']['player_names'] = [player_name]
        self.mediator.gameprops.player_names = [player_name]
        self.mediator.options['settings']['stored_player_names'] = \
            [player_name] + \
            self.mediator.options['settings']['stored_player_names'][1:]
        self.mediator.gameprops.stored_player_names = \
            [player_name] + self.mediator.gameprops.player_names[1:]
        self.mediator.options.store()
        # self.eng.log_mgr.plog(self.season.logic.players)
        # for i, drv in enumerate(self.season.logic.drivers):
        #     dinfo = self.mediator.gameprops.drivers_info[i]
        #     drv.logic.dprops.info = dinfo
        # for drv in self.season.logic.drivers:
        #     if drv.logic.dprops.info.name == player_name:
        #         old_car = drv.logic.dprops.car_name
        # for drv in self.season.logic.drivers:
        #     if drv.logic.dprops.car_name == car:
        #         if drv.logic.dprops.info.name != player_name:
        #             drv.logic.dprops.car_name = old_car
        # for drv in self.season.logic.drivers:
        #     if drv.logic.dprops.info.name == player_name:
        #         drv.logic.dprops.car_name = car
        for player in self.season.logic.players:
            if player.car == car:
                for drv in self.mediator.gameprops.drivers:
                    if drv.img_idx == i:
                        player.driver = drv
        self.__fill_players()
        self.eng.do_later(
            2.0, self.mediator.fsm.demand,
            ['Race', track, self.season.logic.players])

    def __fill_players(self):
        players = self.season.logic.players
        players_car_names = [player.car for player in players]
        remaining_car_names = [
            car for car in self.mediator.gameprops.cars_names
            if car not in players_car_names]
        shuffle(remaining_car_names)
        players_drivers = [player.driver.img_idx for player in players]
        remaining_drivers = [drv for drv in self.mediator.gameprops.drivers
                             if drv.img_idx not in players_drivers]
        shuffle(remaining_drivers)
        num = self.season.props.cars_number - len(players)
        remaining_car_names = remaining_car_names[:num]
        remaining_drivers = remaining_drivers[:num]
        for car, drv in zip(remaining_car_names, remaining_drivers):
            players += [Player(car=car, driver=drv, kind=Player.ai,
                               tuning=TuningPlayer(0, 0, 0))]
        self.season.logic.players = players

    def on_driver_selected_mp(self, track, players):
        #                     player_names, track, cars, drivers):
        # self.mediator.gameprops.player_names = player_names
        # dev = self.mediator.options['development']
        #  self.__bld_players(
        #      self.season.logic.drivers, cars, cars,
        #      self.mediator.options['settings']['cars_number'], 0, 0, 0)
        # sprops = self.__season_props(
        #     self.mediator.gameprops,
        #     self.mediator.options['settings']['cars_number'], True,
        #     dev['race_start_time'], dev['countdown_seconds'],
        #     self.mediator.options['settings']['camera'], 'localmp')
        # sprops.car_names = cars
        # sprops.player_car_names = cars
        #  self.season = SingleRaceSeason(sprops)
        #  # for i, drv in enumerate(self.season.logic.drivers):
        #  #     dinfo = self.mediator.gameprops.drivers_info[i]
        #  #     drv.logic.dprops.info = dinfo
        #  # for idx, (car, drv_idx) in enumerate(zip(cars, drivers)):
        #  #     for drv in self.season.logic.drivers:
        #  #         if drv.logic.dprops.info.img_idx == drv_idx:
        #  #             drv.logic.dprops.player_idx = idx
        #  #     for drv in self.season.logic.drivers:
        #  #         if drv.logic.dprops.info.img_idx == drv_idx:
        #  #             old_car = drv.logic.dprops.car_name
        #  #     for drv in self.season.logic.drivers:
        #  #         if drv.logic.dprops.car_name == car:
        #  #             if drv.logic.dprops.player_idx != idx:
        #  #                 drv.logic.dprops.car_name = old_car
        #  #     for drv in self.season.logic.drivers:
        #  #         if drv.logic.dprops.info.img_idx == drv_idx:
        #  #             drv.logic.dprops.car_name = car
        #  self.season.logic.props.car_names = cars
        #  self.season.attach_obs(self.mediator.event.on_season_end)
        #  self.season.attach_obs(self.mediator.event.on_season_cont)
        #  self.season.start()
        # drivers = sprops.drivers
        # info('drivers: ' + str(drivers))
        # for player in self.season.logic.players:
        #     if player.car == car:
        #         for drv in self.mediator.gameprops.drivers:
        #             if drv.img_idx == i:
        #                 player.driver = drv
        self.season.logic.players = players
        self.__fill_players()
        self.eng.do_later(
            2.0, self.mediator.fsm.demand,
            ['Race', track, self.season.logic.players])

    def on_driver_selected_server(self, player_name, track, car, cars):
        # unused car, cars
        # self.mediator.options['settings']['player_name'] = player_name
        self.mediator.gameprops.player_names = [player_name]
        # self.mediator.options.store()

        packet = [NetMsgs.start_race, len(self.eng.car_mapping)]

        def process(k):
            '''Processes a car.'''
            for addr, carname in self.eng.car_mapping.items():
                if carname == k: return addr
        sprops = self.season.props
        drivers = sprops.drivers
        for k in self.eng.car_mapping.values():
            for _drv in drivers:
                if _drv.dprops.car_name == k:
                    drv = _drv
            packet += [process(k), drv.dprops.info.img_idx,
                       drv.dprops.car_name, drv.dprops.info.name,
                       drv.dprops.info.speed, drv.dprops.info.adherence,
                       drv.dprops.info.stability]
        self.eng.server.send(packet)
        info('start race (on driver): ' + str(packet))
        info('drivers: ' + str(drivers))
        self.eng.do_later(
            2.0, self.mediator.fsm.demand,
            ['Race', track, self.season.logic.players])

    def on_continue(self):
        saved_cars = self.mediator.options['save']['cars']
        dev = self.mediator.options['development']
        tuning = self.mediator.options['save']['tuning']
        # car_tun = tuning[saved_cars]
        drivers = [
            self.__bld_drv(dct, i)
            for i, dct in enumerate(self.mediator.options['save']['drivers'])]
        self.season = Season(self.__season_props(
            self.mediator.gameprops,
            self.mediator.options['settings']['cars_number'], False,
            dev['race_start_time'], dev['countdown_seconds'],
            self.mediator.options['settings']['camera'], 'season'))
        self.season.load(self.mediator.options['save']['ranking'],
                         tuning, drivers)
        self.season.attach_obs(self.mediator.event.on_season_end)
        self.season.attach_obs(self.mediator.event.on_season_cont)
        self.season.start(False)
        track_path = self.mediator.options['save']['track']
        # car_path = self.mediator.options['save']['cars']
        self.mediator.fsm.demand('Race', track_path,
                                 self.season.logic.players, drivers)

    @staticmethod
    def __bld_drv(dct, i):  # unused i
        drv = Driver(
            dct['img_idx'], dct['name'], dct['speed'],
            dct['adherence'], dct['stability'])
        return drv

    def on_race_loaded(self):
        self.season.race.event.detach(self.on_race_loaded)
        self.season.race.results.attach(self.on_race_step)

    def on_race_step(self, race_ranking):
        self.season.race.results.detach(self.on_race_step)
        # ranking = self.season.ranking
        # tuning = self.season.tuning
        if self.season.__class__ != SingleRaceSeason:
            # for car in ranking.carname2points:
            #     ranking.carname2points[car] += race_ranking[car]
            for car in race_ranking.keys():
                for player in self.season.logic.players:
                    if player.car == car:
                        player.points += race_ranking[car]
            # self.mediator.options['save']['ranking'] = \
            #     ranking.carname2points
            # self.mediator.options['save']['tuning'] = tuning.car2tuning
            self.mediator.options['save']['tuning'] = \
                self.season.logic.players
            self.mediator.options.store()
            self.mediator.fsm.demand('Ranking')
        else:
            self.season.logic.notify('on_season_end', True)

    def on_login(self):
        self.init_mp_frm()
        # self.eng.xmpp.send_connected()
        # self.mp_frm.on_users()

    def on_logout(self):
        pass
        # self.mp_frm.on_users()
        # self.mp_frm.on_logout()

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

    def build_race_props(self, players, track_name, keys, joystick,
                         sounds, start_wp, grid):  # unused players
        frwheels = Wheels('EmptyWheelFront', 'EmptyWheelFront.001',
                          'EmptyWheelRear', 'EmptyWheelRear.001')
        # names for front and rear wheels
        bwheels = Wheels('EmptyWheel', 'EmptyWheel.001', 'EmptyWheel.002',
                         'EmptyWheel.003')
        # names for both wheels
        wheel_names = WheelNames(frwheels, bwheels)
        track_gpath = 'assets/tracks/%s/models/track_all.bam' % track_name
        track_fpath = 'assets/tracks/%s/track.json' % track_name
        with open(self.eng.curr_path + track_fpath) as ftrack:
            music_name = load(ftrack)['music']
        music_fpath = 'assets/music/%s.ogg' % music_name
        corner_names = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corner_names = ['Minimap' + crn for crn in corner_names]
        carname2color = self.__car2colors()
        with open(self.eng.curr_path + track_fpath) as ftrack:
            track_cfg = load(ftrack)
            camera_vec = track_cfg['camera_vector']
            shadow_src = track_cfg['shadow_source']
            skidmark_col = track_cfg['skidmark_col']
            laps_num = track_cfg['laps']
        share_urls = [
            'https://www.facebook.com/sharer/sharer.php?u=' +
            'ya2.it/pages/yorg.html',
            'https://twitter.com/share?text=I%27ve%20achieved%20{time}'
            '%20in%20the%20{track}%20track%20on%20Yorg%20by%20%40ya2tech'
            '%21&hashtags=yorg',
            'https://plus.google.com/share?url=ya2.it/pages/yorg.html',
            'https://www.tumblr.com/widgets/share/tool?url=ya2.it']
        # items = self.season.ranking.carname2points.items()
        items = [(player.car, player.points)
                 for player in self.season.logic.players]
        if not grid:
            grid_rev_ranking = sorted(items, key=lambda el: el[1])
            grid = [pair[0] for pair in grid_rev_ranking]
        race_props = RaceProps(
            self.season.props, keys, joystick, sounds,
            'assets/cars/%s/models/capsule', 'Capsule', 'assets/cars',
            wheel_names, 'Road',
            'assets/particles/sparks.ptf',
            self.mediator.options['development']['shaders_dev'],
            self.mediator.options['development']['pbr'],
            self.mediator.options['settings']['shaders'], music_fpath,
            track_gpath, 'assets/tracks/%s/models/collision' % track_name,
            ['Road', 'Offroad'], ['Wall'],
            ['Goal', 'Slow', 'Respawn', 'PitStop'], corner_names,
            WPInfo('Waypoints', 'Waypoint', 'prev'),
            self.mediator.options['development']['show_waypoints'],
            WeaponInfo('Weaponboxs', 'EmptyWeaponboxAnim'), 'Start',
            track_name, 'assets/tracks/' + track_name, 'track', 'Empty',
            'Anim', 'omni', self.sign_cb, 'EmptyNameBillboard4Anim',
            'assets/tracks/%s/images/minimap.txo' % track_name,
            'assets/images/minimaps/car_handle.txo', carname2color,
            camera_vec, shadow_src, laps_num, skidmark_col,
            'assets/models/weapons/rocket/RocketAnim',
            'assets/models/weapons/turbo/TurboAnim',
            'assets/models/weapons/turn/TurnAnim',
            'assets/models/weapons/mine/MineAnim',
            'assets/models/weapons/bonus/WeaponboxAnim', 'Anim',
            self.mediator.options['development']['ai'], InGameMenu,
            share_urls, 'Respawn', 'PitStop', 'Wall', 'Goal', 'Bonus',
            ['Road', 'Offroad'], grid, start_wp,
            self.mediator.options['development']['ai_debug'])
        return race_props

    def __car2colors(self):
        car2col = {}
        cars = [r for r in next(walk(self.eng.curr_path + 'assets/cars'))[1]]
        for car in cars:
            with open(self.eng.curr_path + 'assets/cars/' + car +
                      '/phys.json') as fcar:
                col = tuple(load(fcar)['color'])
            car2col[car] = col
        return car2col
