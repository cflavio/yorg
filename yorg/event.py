from time import strftime
from yyagl.gameobject import Event


class YorgEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', eng.toggle_debug)
        fname = 'yorg_' + strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', eng.base.win.saveScreenshot, [fname])
        base.accept('escape-up', self.mdt.fsm.demand, ['Exit'])

    def on_season_end(self):
        self.mdt.fsm.race.destroy()
        del self.mdt.options['save']
        self.mdt.options.store()
        self.mdt.fsm.demand('Menu')

    def on_season_cont(self, next_track, curr_car, drivers):
        self.mdt.fsm.race.destroy()
        # tuning should go into drivers
        tuning = self.mdt.logic.season.logic.tuning
        self.mdt.options['save']['tuning'] = tuning.logic.to_dct()
        self.mdt.options.store()
        self.mdt.fsm.demand('Race', next_track, curr_car, drivers)
