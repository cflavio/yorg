from sys import exit as sys_exit
from yyagl.gameobject import Fsm
from yyagl.racing.car.audio import CarSounds
from yyagl.racing.car.event import Keys
from menu.menu import YorgMenu, MenuProps
from menu.exitmenu.menu import ExitMenu


class YorgFsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Race', 'Exit'],
            'Race': ['Ranking', 'Menu', 'Exit'],
            'Ranking': ['Tuning', 'Menu', 'Exit'],
            'Tuning': ['Menu', 'Race', 'Exit'],
            'Exit': ['Menu']}
        self.load_txt = self.preview = self.cam_tsk = self.cam_node = \
            self.ranking_texts = self.send_tsk = self.cam_pivot = \
            self.ready_clients = self.curr_load_txt = self.__menu = \
            self.race = self.__exit_menu = None

    def enterMenu(self):
        self.eng.log_mgr.log('entering Menu state')
        menu_props = MenuProps(
            self.mdt.gameprops, self.mdt.options,
            self.mdt.options['development']['multiplayer'],
            'assets/images/gui/yorg_title.png',
            'http://feeds.feedburner.com/ya2tech?format=xml',
            'http://www.ya2.it', 'save' in self.mdt.options.dct,
            'http://www.ya2.it/support-us')
        self.__menu = YorgMenu(menu_props)
        methods = [self.mdt.logic.on_input_back,
                   self.mdt.logic.on_options_back,
                   self.mdt.logic.on_car_selected,
                   self.mdt.logic.on_car_selected_season,
                   self.mdt.logic.on_driver_selected,
                   self.mdt.logic.on_continue]
        map(self.__menu.attach_obs, methods)
        self.__menu.attach_obs('on_exit', redirect=self.demand, args=['Exit'])
        self.mdt.audio.menu_music.play()
        if self.mdt.logic.season:
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_end)
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_cont)

    def exitMenu(self):
        self.eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', drivers=''):
        self.eng.log_mgr.log('entering Race state')
        base.ignore('escape-up')
        if 'save' not in self.mdt.options.dct:
            self.mdt.options['save'] = {}
        seas = self.mdt.logic.season
        if not seas.props.single_race:
            self.mdt.options['save']['track'] = track_path
            self.mdt.options['save']['car'] = car_path
            self.mdt.options['save']['drivers'] = drivers
            self.mdt.options['save']['tuning'] = seas.tuning.car2tuning
            self.mdt.options['save']['ranking'] = seas.ranking.carname2points
            self.mdt.options.store()
        keys = self.mdt.options['settings']['keys']
        keys = Keys(keys['forward'], keys['rear'], keys['left'], keys['right'],
                    keys['fire'], keys['respawn'], keys['pause'])
        joystick = self.mdt.options['settings']['joystick']
        sounds = CarSounds(
            'assets/sfx/engine.ogg', 'assets/sfx/brake.ogg',
            'assets/sfx/crash.ogg', 'assets/sfx/crash_high_speed.ogg',
            'assets/sfx/lap.ogg', 'assets/sfx/landing.ogg')
        race_props = self.mdt.logic.build_race_props(
            seas.logic.drivers, track_path, keys, joystick, sounds)
        if self.eng.server.is_active:
            self.season.create_race_server(race_props)
        elif self.eng.client.is_active:
            self.season.create_race_client(race_props)
        else:
            seas.create_race(race_props)
        self.eng.log_mgr.log('selected drivers: ' + str(drivers))
        seas.race.logic.drivers = drivers
        track_name_transl = track_path
        track_dct = {'desert': _('desert'), 'mountain': _('mountain'),
                     'amusement': _('amusement park'),
                     'countryside': _('countryside')}
        if track_path in track_dct:
            track_name_transl = track_dct[track_path]
        seas.race.fsm.demand(
            'Loading', race_props, track_name_transl, drivers)
        seas.race.attach_obs(self.mdt.logic.on_race_loaded)
        exit_mth = 'on_ingame_exit_confirm'
        seas.race.attach_obs(exit_mth, redirect=self.mdt.fsm.demand,
                             args=['Menu'])

    def exitRace(self):
        self.eng.log_mgr.log('exiting Race state')
        self.mdt.logic.season.race.destroy()
        base.accept('escape-up', self.demand, ['Exit'])

    def enterRanking(self):
        self.mdt.logic.season.ranking.show(
            self.mdt.logic.season.race.logic.props,
            self.mdt.logic.season.props)
        self.eng.do_later(.1, self.mdt.logic.season.ranking.attach_obs,
                          [self.on_ranking_end])

    def on_ranking_end(self):
        self.demand('Tuning')

    def exitRanking(self):
        self.mdt.logic.season.ranking.detach_obs(self.on_ranking_end)
        self.mdt.logic.season.ranking.hide()

    def enterTuning(self):
        self.mdt.logic.season.tuning.show_gui()

    def exitTuning(self):
        self.mdt.logic.season.tuning.hide_gui()

    def enterExit(self):
        if not self.mdt.options['development']['show_exit']:
            sys_exit()
        self.__exit_menu = ExitMenu(self.mdt.gameprops.menu_args)
        base.accept('escape-up', self.demand, ['Menu'])

    def exitExit(self):
        self.__exit_menu.destroy()
        base.accept('escape-up', self.demand, ['Exit'])
