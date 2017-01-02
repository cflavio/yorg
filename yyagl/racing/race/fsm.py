from yyagl.gameobject import Fsm
from yyagl.racing.race.gui.countdown import Countdown



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
        if game.options['development']['shaders']:
            eng.shader_mgr.toggle_shader()
        map(lambda car: car.fsm.demand('Countdown'), [game.player_car] + game.cars)

    def exitCountdown(self):
        self.countdown.destroy()

    def enterPlay(self):
        eng.log_mgr.log('entering Play state')
        map(lambda car: car.fsm.demand('Play'), [game.player_car] + game.cars)

    def on_start_race(self):
        self.mdt.fsm.demand('Play')

    def exitPlay(self):
        eng.log_mgr.log('exiting Play state')

    def enterResults(self, race_ranking):
        game.fsm.race.gui.results.show(race_ranking)
        map(lambda car: car.fsm.demand('Results'), [game.player_car] + game.cars)

    def exitResults(self):
        self.mdt.logic.exit_play()
        if game.options['development']['shaders']:
            eng.shader_mgr.toggle_shader()
