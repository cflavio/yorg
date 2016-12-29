from racing.game.gameobject import Logic


class TuningLogic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.tuning = {}
        self.reset()

    def reset(self):
        self.tuning = {'engine': 0, 'tires': 0, 'suspensions': 0}

    def load(self, tuning):
        self.tuning = tuning
