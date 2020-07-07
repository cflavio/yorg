from time import strftime
from yyagl.gameobject import EventColleague


class YorgEvent(EventColleague):

    def __init__(self, mediator):
        EventColleague.__init__(self, mediator)
        if not self.eng.is_runtime:
            self.accept('f12', self.eng.phys_mgr.toggle_dbg)
        fname = 'yorg_' + strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', base.win.saveScreenshot, [fname])
        base.accept('escape-up', self.mediator.fsm.demand, ['Exit'])
        if not self.eng.is_runtime:
            self.accept('f9', self.eng.profiler.toggle)

    def on_season_end(self, singlerace=False):
        if not singlerace:
            del self.mediator.options['save']
            self.mediator.options.store()
        self.mediator.fsm.demand('Menu')
        # self.mediator.logic.season.race.destroy()
        self.mediator.logic.season = self.mediator.logic.season.destroy()

    def on_season_cont(self, next_track, curr_car, players):
        # unused curr_car
        self.mediator.logic.season.race.destroy()
        # tuning = self.mediator.logic.season.tuning
        # self.mediator.options['save']['tuning'] = tuning.to_dct
        stored_players = [player.to_json() for player in players]
        self.mediator.options['save']['players'] = stored_players
        self.mediator.options.store()
        self.mediator.fsm.demand('Race', next_track, players)
