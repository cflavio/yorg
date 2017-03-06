from yyagl.racing.race.race import RaceSinglePlayer, RaceServer, RaceClient
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

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', player_cars=[],
                  drivers=''):
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
            tuning = self.mdt.logic.season.logic.tuning.logic.tuning
            self.race = RaceSinglePlayer(
                keys, joystick, sounds, (.75, .75, .25, 1), (.75, .75, .75, 1),
                'assets/fonts/Hanken-Book.ttf', 'capsule', 'Capsule',
                'assets/models/cars', 'phys.yml', wheel_names,
                tuning['engine'], tuning['tires'], tuning['suspensions'],
                'Road', 'assets/models/cars', 'car',
                ['cardamage1', 'cardamage2'],
                ['wheelfront', 'wheelrear', 'wheel'],
                'assets/particles/sparks.ptf')  # use global template args
        eng.log_mgr.log('selected drivers: ' + str(drivers))
        self.race.logic.drivers = drivers
        self.race.fsm.demand('Loading', track_path, car_path, player_cars,
                             drivers)

    def exitRace(self):
        eng.log_mgr.log('exiting Race state')
        self.race.destroy()

    def enterRanking(self):
        game.logic.season.logic.ranking.gui.show()

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
