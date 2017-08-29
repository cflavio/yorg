from sys import exit as sys_exit
from yyagl.gameobject import Fsm
from yyagl.engine.network.server import Server
from yyagl.engine.network.client import Client
from yyagl.engine.log import LogMgr
from yyagl.racing.car.audio import CarSounds
from yyagl.racing.car.event import Keys
from menu.menu import YorgMenu, MenuProps
from menu.exitmenu.menu import ExitMenu
from .thanksnames import ThanksNames


class YorgFsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Race', 'Exit'],
            'Race': ['Ranking', 'Menu', 'Exit'],
            'Ranking': ['Tuning', 'Menu', 'Exit'],
            'Tuning': ['Menu', 'Race', 'Exit'],
            'Exit': ['Menu']}
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
        LogMgr().log('entering Menu state')
        cars_names = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                      'iperion', 'teia']
        menu_props = MenuProps(
            self.mdt.gameprops.menu_args, self.mdt.options,
            cars_names[:int(self.mdt.options['settings']['cars_number'])],
            'assets/images/cars/%s.png',
            eng.curr_path + 'assets/models/cars/%s/phys.yml',
            ['desert', 'mountain', 'amusement', 'countryside'],
            lambda: [_('desert'), _('mountain'), _('amusement park'),
                     _('countryside')],
            'assets/images/tracks/%s.png',
            self.mdt.options['settings']['player_name'],
            ['assets/images/drivers/driver%s.png',
             'assets/images/drivers/driver%s_sel.png'],
            'assets/images/cars/%s_sel.png',
            self.mdt.options['development']['multiplayer'],
            'assets/images/gui/yorg_title.png',
            'http://feeds.feedburner.com/ya2tech?format=xml',
            'http://www.ya2.it', 'save' in self.mdt.options.dct,
            ['desert', 'mountain', 'amusement', 'countryside'],
            'http://www.ya2.it/support-us', self.__drivers())
        self.__menu = YorgMenu(menu_props)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_input_back)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_options_back)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_car_selected)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_car_selected_season)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_driver_selected)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_exit)
        self.__menu.gui.menu.attach_obs(self.mdt.logic.on_continue)
        self.mdt.logic.menu_start()
        if self.mdt.logic.season:
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_end)
            self.mdt.logic.season.detach_obs(self.mdt.event.on_season_cont)

    def __drivers(self):  # NB duplicate of the one in season_props()
        names = ThanksNames.get_thanks(8, 5)
        drivers = [
            (1, names[0], (4, -2, -2)),
            (2, names[1], (-2, 4, -2)),
            (3, names[2], (0, 4, -4)),
            (4, names[3], (4, -4, 0)),
            (5, names[4], (-2, -2, 4)),
            (6, names[5], (-4, 0, 4)),
            (7, names[6], (4, 0, -4)),
            (8, names[7], (-4, 4, 0))]
        cars = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                'iperion', 'teia']
        for i, _car in enumerate(cars):
            drivers[i] = drivers[i] + (_car, )
        return drivers

    def exitMenu(self):
        LogMgr().log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', drivers=''):
        LogMgr().log('entering Race state')
        base.ignore('escape-up')
        if 'save' not in self.mdt.options.dct:
            self.mdt.options['save'] = {}
        if not self.mdt.logic.season.props.single_race:
            self.mdt.options['save']['track'] = track_path
            self.mdt.options['save']['car'] = car_path
            self.mdt.options['save']['drivers'] = drivers
            self.mdt.options['save']['tuning'] = self.mdt.logic.season.tuning.car2tuning
            self.mdt.options['save']['ranking'] = self.mdt.logic.season.ranking.carname2points
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
            car_path, drivers, track_path, keys, joystick, sounds)
        if Server().is_active:
            self.season.create_race_server(race_props)
        elif Client().is_active:
            self.season.create_race_client(race_props)
        else:
            self.mdt.logic.season.create_race(race_props,
                                              self.mdt.logic.season.props)
        LogMgr().log('selected drivers: ' + str(drivers))
        self.mdt.logic.season.race.logic.drivers = drivers
        track_name_transl = track_path
        track_dct = {'desert': _('desert'), 'mountain': _('mountain'),
                     'amusement': _('amusement park'),
                     'countryside': _('countryside')}
        if track_path in track_dct:
            track_name_transl = track_dct[track_path]
        self.mdt.logic.season.race.fsm.demand(
            'Loading', race_props, self.mdt.logic.season.props,
            track_name_transl, drivers)
        self.mdt.logic.season.race.attach_obs(self.mdt.logic.on_race_loaded)
        exit_meth = self.mdt.logic.on_ingame_exit_confirm
        self.mdt.logic.season.race.attach_obs(exit_meth)

    def exitRace(self):
        LogMgr().log('exiting Race state')
        self.mdt.logic.season.race.destroy()
        base.accept('escape-up', self.demand, ['Exit'])

    def enterRanking(self):
        self.mdt.logic.season.ranking.show(
            self.mdt.logic.season.race.logic.props, self.mdt.logic.season.props)
        eng.do_later(.1, self.mdt.logic.season.ranking.attach_obs, [self.on_ranking_end])

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
