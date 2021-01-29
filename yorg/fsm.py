from logging import info
from sys import exit as sys_exit
from os.path import exists
from yyagl.dictfile import DctFile
from yyagl.gameobject import FsmColleague
from yracing.car.audio import CarSounds
from yracing.car.event import Keys, PlayerKeys
from yracing.player.player import Player
from menu.menu import YorgMenu, MenuProps
from menu.exitmenu.menu import ExitMenu


class YorgFsm(FsmColleague):

    def __init__(self, mediator):
        FsmColleague.__init__(self, mediator)
        self.__menu_props = None
        self.defaultTransitions = {
            'Menu': ['Race', 'Exit'],
            'Race': ['Ranking', 'Menu', 'Exit'],
            'Ranking': ['Tuning', 'Menu', 'Exit'],
            'Tuning': ['Menu', 'Race', 'Exit'],
            'Exit': ['Menu']}
        self.load_txt = self.preview = self.cam_tsk = self.cam_node = \
            self.ranking_texts = self.send_tsk = self.cam_pivot = \
            self.ready_clients = self.curr_load_txt = self.menu = \
            self.race = self.__exit_menu = self.loader_tsk = \
            self.models = None

    def enterMenu(self):
        info('entering Menu state')
        self.mediator.reset_drivers()
        self.mediator.gameprops.player_names = \
            self.mediator.options['settings']['player_names']
        self.mediator.gameprops.stored_player_names = \
            self.mediator.options['settings']['stored_player_names']
        self.__menu_props = MenuProps(
            self.mediator.gameprops, self.mediator.options,
            'assets/images/gui/yorg_title.txo',
            'http://feeds.feedburner.com/ya2tech?format=xml',
            'https://www.ya2.it', 'save' in self.mediator.options.dct,
            'https://www.ya2.it/pages/support_us.html')
        self.menu = YorgMenu(self.__menu_props)
        methods = [self.mediator.logic.on_input_back,
                   self.mediator.logic.on_options_back,
                   self.mediator.logic.on_room_back,
                   self.mediator.logic.on_quit,
                   self.mediator.logic.on_car_selected,
                   self.mediator.logic.on_car_selected_mp,
                   self.mediator.logic.on_car_selected_omp_srv,
                   self.mediator.logic.on_car_selected_omp_client,
                   self.mediator.logic.on_car_start_client,
                   self.mediator.logic.on_car_selected_season,
                   self.mediator.logic.on_driver_selected,
                   self.mediator.logic.on_driver_selected_server,
                   self.mediator.logic.on_driver_selected_mp,
                   self.mediator.logic.on_track_selected,
                   self.mediator.logic.on_track_selected_mp,
                   self.mediator.logic.on_continue,
                   self.mediator.logic.on_login,
                   self.mediator.logic.on_logout,
                   self.mediator.logic.on_single_race,
                   self.mediator.logic.on_start_season,
                   self.mediator.logic.on_start_local_mp,
                   self.mediator.logic.on_start_mp_server,
                   self.mediator.logic.on_start_mp_client]
        list(map(self.menu.attach_obs, methods))
        self.menu.attach_obs(self.demand, rename='on_exit', args=['Exit'])
        self.mediator.audio.menu_music.play()
        if self.mediator.logic.season:
            self.mediator.logic.season.detach_obs(
                self.mediator.event.on_season_end)
            self.mediator.logic.season.detach_obs(
                self.mediator.event.on_season_cont)
        self.models = []
        for car in self.mediator.gameprops.cars_names:
            self.models += [self.mediator.gameprops.damage_paths.low % car]
            self.models += [self.mediator.gameprops.damage_paths.hi % car]
            self.models += [self.mediator.gameprops.model_name % car]

            fpath = self.mediator.gameprops.wheel_gfx_names.front % car
            rpath = self.mediator.gameprops.wheel_gfx_names.rear % car
            m_exists = lambda path: \
                exists(path + '.egg') or exists(path + '.bam')
            b_path = self.mediator.gameprops.wheel_gfx_names.both % car
            front_path = fpath if m_exists(fpath) else b_path
            rear_path = rpath if m_exists(rpath) else b_path
            self.models += [front_path]
            self.models += [rear_path]
        self.load_models(None)
        self.eng.client.attach(self.on_presence_unavailable_room)
        # if self.mediator.logic.mp_frm:
        #     #if self.eng.xmpp.client:  # if we're logged
        #     #    self.mediator.logic.mp_frm.send_is_playing(False)
        #     self.mediator.logic.mp_frm.users_frm.invited_users = []
        #     self.mediator.logic.mp_frm.users_frm.in_match_room = None
        #     self.mediator.logic.mp_frm.msg_frm.curr_match_room = None

    def on_presence_unavailable_room(self, uid, room_name):
        # unused uid, room_name
        # for usr in self.eng.xmpp.users:
        #     if usr.name == uid:
        #         if self.eng.server.is_active:
        #             for conn in self.eng.server.connections[:]:
        #                 if usr.public_addr == conn.getpeername() or \
        #                         usr.local_addr == conn.getpeername():
        #                     self.eng.server.connections.remove(conn)
        if self.getCurrentOrNextState() == 'Menu':
            pass
            # if uid == self.mediator.logic.mp_frm.users_frm.in_match_room:
            #     self.menu.disable()

    def on_start_match(self):
        self.menu.logic.on_push_page(
            'trackpageserver',
            [self.__menu_props, self.mediator.fsm.menu.logic.curr_room])

    def on_start_match_client(self, track):
        # self.mediator.logic.mp_frm.on_track_selected()
        self.menu.logic.on_track_selected(track)
        self.menu.logic.on_push_page('carpageclient', [self.__menu_props])

    def enable_menu(self, val):
        (self.menu.enable if val else self.menu.disable)()

    def enable_menu_navigation(self, val):
        (self.menu.enable_navigation if val else
         self.menu.disable_navigation)()

    def on_srv_quitted(self):
        if self.getCurrentOrNextState() == 'Menu':
            self.menu.logic.on_srv_quitted()
        else: self.demand('Menu')

    def on_removed(self): self.menu.logic.on_removed()

    # def create_room(self, room, nick):
    #     self.menu.logic.create_room(room, nick)

    def load_models(self, model):
        if not self.models: return
        model = self.models.pop(0)
        self.loader_tsk = loader.loadModel(model, callback=self.load_models)

    def exitMenu(self):
        info('exiting Menu state')
        self.menu.destroy()
        self.mediator.audio.menu_music.stop()
        loader.cancelRequest(self.loader_tsk)
        self.eng.client.detach(self.on_presence_unavailable_room)

    def enterRace(self, track_path='', players=None, ranking=None):
        # unused ranking
        info('entering Race state')
        #if self.mediator.logic.mp_frm:  # None if dev quicksart
        #    self.mediator.logic.mp_frm.hide()
        players = players or []
        players = [player.to_json() for player in players]
        base.ignore('escape-up')
        seas = self.mediator.logic.season
        if not seas.props.single_race:
            if 'save' not in self.mediator.options.dct:
                self.mediator.options['save'] = {}
            self.mediator.options['save']['track'] = track_path
            # self.mediator.options['save']['cars'] = car_path
            # self.mediator.options['save']['drivers'] = [
            #     drv.to_dct() for drv in drivers]
            # self.mediator.options['save']['tuning'] = seas.tuning.car2tuning
            self.mediator.options['save']['players'] = seas.logic.players
            # self.mediator.options['save']['ranking'] = \
            #     seas.ranking.carname2points
            players = self.mediator.options['save']['players']
            players = [player.to_json() for player in players]
            self.mediator.options['save']['players'] = players
            self.mediator.options.store()
        keys = self.mediator.options['settings']['keys']
        joystick = self.mediator.options['settings']['joystick']
        p1k = PlayerKeys(keys['forward1'], keys['rear1'], keys['left1'],
                         keys['right1'], keys['fire1'], keys['respawn1'])
        p2k = PlayerKeys(keys['forward2'], keys['rear2'], keys['left2'],
                         keys['right2'], keys['fire2'], keys['respawn2'])
        p3k = PlayerKeys(keys['forward3'], keys['rear3'], keys['left3'],
                         keys['right3'], keys['fire3'], keys['respawn3'])
        p4k = PlayerKeys(keys['forward4'], keys['rear4'], keys['left4'],
                         keys['right4'], keys['fire4'], keys['respawn4'])
        keys = Keys([p1k, p2k, p3k, p4k])
        sounds = CarSounds(
            'assets/sfx/engine.ogg', 'assets/sfx/brake.ogg',
            'assets/sfx/crash.ogg', 'assets/sfx/crash_high_speed.ogg',
            'assets/sfx/lap.ogg', 'assets/sfx/landing.ogg',
            'assets/sfx/pitstop.ogg', 'assets/sfx/fire.ogg',
            'assets/sfx/hit.ogg', 'assets/sfx/turbo.ogg',
            'assets/sfx/rotate_all_fire.ogg', 'assets/sfx/rotate_all_hit.ogg')
        grid = [player.car for player in seas.logic.players]
        race_props = self.mediator.logic.build_race_props(
            seas.logic.players, track_path, keys, joystick, sounds,
            self.mediator.options['development']['start_wp'], grid)
        if self.eng.server.is_active:
            # seas.create_race_server(race_props)
            seas.create_race_server(
                race_props, [Player.from_json(player) for player in players])
        elif self.eng.client.is_client_active:
            seas.create_race_client(
                race_props, [Player.from_json(player) for player in players])
        else:
            seas.create_race(
                race_props, [Player.from_json(player) for player in players])
        track_dct = {
            'toronto': _('Toronto'), 'rome': _('Rome'),
            'sheffield': _('Sheffield'), 'orlando': _('Orlando'),
            'nagano': _('Nagano'), 'dubai': _('Dubai'),
            'moon': _('Sinus Aestuum')}
        track_name_transl = track_dct.get(track_path, track_path)
        seas.race.fsm.demand(
            'Loading', race_props, track_name_transl, seas.ranking,
            seas.logic.players)
        seas.race.attach_obs(self.mediator.logic.on_race_loaded)
        exit_mth = 'on_ingame_exit_confirm'
        seas.race.attach_obs(self.mediator.fsm.demand, rename=exit_mth,
                             args=['Menu'])
        self.eng.client.attach(self.on_presence_unavailable_room)

    def exitRace(self):
        info('exiting Race state')
        dev = self.mediator.options['development']
        # cars = dev['cars'] if 'cars' in dev else ''
        # track = dev['track'] if 'track' in dev else ''
        # server = dev['server'] if 'server' in dev else ''
        # if not (cars and track and not server):
        #     self.mediator.logic.mp_frm.show()
        self.mediator.logic.season.race.destroy()
        for i in range(4):
            self.eng.joystick_mgr.joystick_lib.clear_vibration(i)
        base.accept('escape-up', self.demand, ['Exit'])
        self.eng.client.detach(self.on_presence_unavailable_room)

    def enterRanking(self):
        self.mediator.logic.season.ranking.show(
            self.mediator.logic.season.race.logic.props,
            self.mediator.logic.season.props,
            self.mediator.logic.season.logic.ranking,
            self.mediator.logic.season.logic.players)
        self.eng.do_later(.1, self.mediator.logic.season.ranking.attach_obs,
                          [self.on_ranking_end])
        self.eng.do_later(.1, self.mediator.logic.season.ranking.attach_obs,
                          [self.on_ranking_next_race])

    def on_ranking_end(self, players):
        self.demand('Tuning', players)

    def on_ranking_next_race(self):
        self.mediator.logic.season.logic.next_race()

    def exitRanking(self):
        self.mediator.logic.season.ranking.detach_obs(self.on_ranking_end)
        self.mediator.logic.season.ranking.detach_obs(
            self.on_ranking_next_race)
        self.mediator.logic.season.ranking.hide()

    def enterTuning(self, players):
        self.mediator.logic.season.tuning.show_gui(players)

    def exitTuning(self):
        self.mediator.logic.season.tuning.hide_gui()

    def enterExit(self):
        if not self.mediator.options['development']['show_exit']:
            # self.eng.xmpp.destroy()
            sys_exit()
        self.__exit_menu = ExitMenu(self.mediator.gameprops.menu_props)
        base.accept('escape-up', self.demand, ['Menu'])

    def exitExit(self):
        self.__exit_menu.destroy()
        base.accept('escape-up', self.demand, ['Exit'])
