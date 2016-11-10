from racing.game.game import GameLogic


class YorgLogic(GameLogic):

    def __init__(self, mdt):
        GameLogic.__init__(self, mdt)
        self.season = None

    def on_start(self):
        GameLogic.on_start(self)
        dev = game.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        if car and track:
            self.mdt.fsm.demand('Race', 'tracks/' + track, car)
        else:
            self.mdt.fsm.demand('Menu')
