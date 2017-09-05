from time import strftime
from yyagl.gameobject import Event
from yyagl.engine.phys import PhysMgr


class YorgEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        if not self.eng.is_runtime:
            self.accept('f12', self.eng.phys_mgr.toggle_debug)
        fname = 'yorg_' + strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', self.eng.base.win.saveScreenshot, [fname])
        base.accept('escape-up', self.mdt.fsm.demand, ['Exit'])
        if not self.eng.is_runtime:
            self.accept('f9', self.eng.profiler.toggle)

    def on_season_end(self, singlerace=False):
        if not singlerace:
            del self.mdt.options['save']
            self.mdt.options.store()
        self.mdt.fsm.demand('Menu')
        self.mdt.logic.season.race.destroy()
        self.mdt.logic.season = self.mdt.logic.season.destroy()

    def on_season_cont(self, next_track, curr_car, drivers):
        self.mdt.logic.season.race.destroy()
        tuning = self.mdt.logic.season.tuning
        self.mdt.options['save']['tuning'] = tuning.to_dct
        self.mdt.options.store()
        self.mdt.fsm.demand('Race', next_track, curr_car, drivers)
