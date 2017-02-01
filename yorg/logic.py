from yyagl.game import GameLogic
from yyagl.racing.season.season import SingleRaceSeason


class YorgLogic(GameLogic):

    def __init__(self, mdt):
        GameLogic.__init__(self, mdt)
        self.season = None

    def on_start(self):
        GameLogic.on_start(self)
        dev = game.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        drivers = [(1, 'first name', 'kronos'), (2, 'second name', 'themis'),
                   (3, 'third name', 'diones'), (4, 'fourth name', 'iapeto')]
        if car and track:
            game.logic.season = SingleRaceSeason()
            self.mdt.fsm.demand('Race', 'tracks/' + track, car, [], drivers)
        else:
            self.mdt.fsm.demand('Menu')
