from racing.race.race import Race
from racing.game.gameobject import Fsm
from menu.menu import YorgMenu


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Loading'],
            'Loading': ['Play'],
            'Play': ['Ranking', 'Menu'],
            'Ranking': ['Play', 'Menu', 'Loading']}
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

    def enterLoading(self, track_path='', car_path='', player_cars=[]):
        eng.log_mgr.log('entering Loading state')
        self.race = Race()
        self.race.logic.enter_loading(track_path, car_path, player_cars)

    def exitLoading(self):
        eng.log_mgr.log('exiting Loading state')
        self.race.logic.exit_loading()

    def enterPlay(self):
        eng.log_mgr.log('entering Play state')
        self.race.logic.enter_play()

    def exitPlay(self):
        eng.log_mgr.log('exiting Play state')
        self.race.logic.exit_play()

    def enterRanking(self):
        game.logic.season.logic.ranking.gui.show()

    def exitRanking(self):
        game.logic.season.logic.ranking.gui.destroy()
