from yyagl.racing.race.race import Race, RaceSinglePlayer, RaceServer, \
    RaceClient
from yyagl.gameobject import Fsm
from yyagl.engine.gui.page import PageGui
from menu.menu import YorgMenu
from menu.exitmenu.menu import ExitMenu
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
import sys
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import WindowProperties


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

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = YorgMenu()
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', player_cars=[], drivers=''):
        eng.log_mgr.log('entering Race state')
        if eng.server.is_active:
            self.race = RaceServer()
        elif eng.client.is_active:
            self.race = RaceClient()
        else:
            self.race = RaceSinglePlayer()
        eng.log_mgr.log('selected drivers: ' + str(drivers))
        self.race.logic.drivers = drivers
        self.race.fsm.demand('Loading', track_path, car_path, player_cars, drivers)

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
