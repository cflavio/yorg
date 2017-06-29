from time import strftime
from yyagl.gameobject import Event
from yyagl.engine.phys import PhysMgr
from yyagl.engine.profiler import Profiler


class YorgEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', PhysMgr().toggle_debug)
        fname = 'yorg_' + strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', eng.base.win.saveScreenshot, [fname])
        base.accept('escape-up', self.mdt.fsm.demand, ['Exit'])
        self.accept('f9', Profiler().toggle)

    def on_season_end(self):
        self.mdt.logic.season.race.destroy()
        del self.mdt.options['save']
        self.mdt.options.store()
        self.mdt.fsm.demand('Menu')

    def on_season_cont(self, next_track, curr_car, drivers):
        self.mdt.logic.season.race.destroy()
        tuning = self.mdt.logic.season.tuning
        self.mdt.options['save']['tuning'] = tuning.to_dct()
        self.mdt.options.store()
        self.mdt.fsm.demand('Race', next_track, curr_car, drivers)
