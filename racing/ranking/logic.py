from racing.game.gameobject import Logic


class _Logic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.ranking = {}
        self.reset()

    def reset(self):
        self.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}

    def load(self, ranking):
        self.ranking = ranking
