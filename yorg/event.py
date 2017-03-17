import time
from yyagl.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', eng.phys.toggle_debug)
        fname = 'yorg_' + time.strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', eng.base.win.saveScreenshot, [fname])
        base.accept('escape-up', game.fsm.demand, ['Exit'])

    def on_season_end(self):
        game.fsm.race.destroy()
        del game.options['save']
        game.options.store()
        game.fsm.demand('Menu')

    def on_season_cont(self, next_track, curr_car, drivers, skills):
        game.fsm.race.destroy()
        tuning = game.logic.season.logic.tuning
        game.options['save']['tuning'] = tuning.logic.to_dct()
        game.options.store()
        game.fsm.demand('Race', next_track, curr_car, drivers, skills)
