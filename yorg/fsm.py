from yyagl.racing.race.race import Race, RaceSinglePlayer, RaceServer, \
    RaceClient
from yyagl.gameobject import Fsm
from menu.menu import YorgMenu


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Race'],
            'Race': ['Ranking', 'Menu'],
            'Ranking': ['Tuning'],
            'Tuning': ['Menu', 'Race']}
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

    def enterRace(self, track_path='', car_path='', player_cars=[], driver=''):
        eng.log_mgr.log('entering Race state')
        if eng.server.is_active:
            self.race = RaceServer()
        elif eng.client.is_active:
            self.race = RaceClient()
        else:
            self.race = RaceSinglePlayer()
        eng.log_mgr.log('selected driver: ' + driver)
        self.race.fsm.demand('Loading', track_path, car_path, player_cars)

    def exitRace(self):
        self.race.destroy()

    def enterRanking(self):
        game.logic.season.logic.ranking.gui.show()

    def exitRanking(self):
        game.logic.season.logic.ranking.gui.hide()

    def enterTuning(self):
        game.logic.season.logic.tuning.gui.show()

    def exitTuning(self):
        game.logic.season.logic.tuning.gui.hide()
