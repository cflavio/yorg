from racing.game.gameobject import Logic
from racing.ranking.ranking import Ranking
from racing.race.race import Race


class SeasonLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.ranking = Ranking()

    def start(self):
        self.ranking.logic.reset()

    def load(self):
        self.ranking.logic.load(game.options['save']['ranking'])

    @staticmethod
    def step():
        current_track = game.track.path[7:]
        tracks = ['prototype', 'desert']
        game.fsm.race.destroy()
        if tracks.index(current_track) == len(tracks) - 1:
            del game.options['save']
            game.options.store()
            game.fsm.demand('Menu')
        else:
            next_track = tracks[tracks.index(current_track) + 1]
            curr_car = game.options['save']['car']
            game.fsm.demand('Race', 'tracks/' + next_track, curr_car)


class SingleRaceSeasonLogic(SeasonLogic):

    @staticmethod
    def step():
        game.fsm.demand('Menu')
