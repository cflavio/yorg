from racing.game.gameobject import Fsm
from racing.race.gui.countdown import Countdown



class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Loading': ['Countdown'],
            'Countdown': ['Play'],
            'Play': ['Results']}

    def enterLoading(self, track_path='', car_path='', player_cars=[]):
        eng.log_mgr.log('entering Loading state')
        args = [track_path, car_path, player_cars]
        self.mdt.gui.loading.enter_loading(*args)
        taskMgr.doMethodLater(1.0, self.mdt.logic.load_stuff, 'loading stuff', args)

    def exitLoading(self):
        eng.log_mgr.log('exiting Loading state')
        self.mdt.gui.loading.exit_loading()

    def enterCountdown(self):
        self.countdown = Countdown()
        self.countdown.attach(self.on_start_race)
        self.mdt.logic.enter_play()

    def exitCountdown(self):
        self.countdown.destroy()

    def enterPlay(self):
        eng.log_mgr.log('entering Play state')

    def on_start_race(self):
        self.mdt.fsm.demand('Play')

    def exitPlay(self):
        eng.log_mgr.log('exiting Play state')

    def enterResults(self, race_ranking):
        game.fsm.race.gui.results.show(race_ranking)

    def exitResults(self):
        self.mdt.logic.exit_play()
