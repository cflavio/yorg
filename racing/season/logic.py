from racing.game.gameobject.gameobject import Logic
from racing.ranking.ranking import Ranking
from racing.race.race import Race


class _Logic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.ranking = Ranking()

    def start(self):
        self.ranking.logic.reset()

    def load(self):
        self.ranking.logic.load(game.options['save']['ranking'])
        game.race = Race()
        game.race.logic.start()
