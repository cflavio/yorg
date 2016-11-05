from racing.game.gameobject import Logic


class RankingLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.ranking = {}
        self.reset()

    def reset(self):
        self.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}

    def load(self, ranking):
        self.ranking = ranking

    @staticmethod
    def step():
        current_track = game.track.gfx.track_path[7:]
        tracks = ['prototype', 'desert']
        if tracks.index(current_track) == len(tracks) - 1:
            game.ranking = None
            conf = game.options
            del conf['save']
            conf.store()
            game.fsm.demand('Menu')
        else:
            next_track = tracks[tracks.index(current_track) + 1]
            curr_car = game.options['save']['car']
            game.fsm.demand('Loading', 'tracks/' + next_track, curr_car)
