from random import shuffle
from yyagl.game import GameLogic
from yyagl.racing.season.season import SingleRaceSeason, SeasonProps


class YorgLogic(GameLogic):

    def __init__(self, mdt):
        GameLogic.__init__(self, mdt)
        self.season = None

    def on_start(self):
        GameLogic.on_start(self)
        dev = game.options['development']
        car = dev['car'] if 'car' in dev else ''
        track = dev['track'] if 'track' in dev else ''
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:9]
        self.drivers = [
            (1, names[0], (4, -2, -2)),
            (2, names[1], (-2, 4, -2)),
            (3,  names[2], (0, 4, -4)),
            (4,  names[3], (4, -4, 0)),
            (5,  names[4], (-2, -2, 4)),
            (6,  names[5], (-4, 0, 4)),
            (7,  names[6], (4, 0, -4)),
            (8,  names[7], (-4, 4, 0))]
        cars = ['kronos', 'themis', 'diones', 'iapeto', '', '', '', '']
        for i, _car in enumerate(cars):
          self.drivers[i] = self.drivers[i] + (_car, )
        if car and track:
            season_props = SeasonProps(
                ['kronos', 'themis', 'diones', 'iapeto'], car, self.drivers,
                'assets/images/gui/menu_background.jpg',
                ['assets/images/tuning/engine.png',
                 'assets/images/tuning/tires.png',
                 'assets/images/tuning/suspensions.png'],
                ['prototype', 'desert'],
                'assets/fonts/Hanken-Book.ttf', (.75, .75, .75, 1))
            self.season = SingleRaceSeason(season_props)
            self.season.attach_obs(self.mdt.event.on_season_end)
            self.season.attach_obs(self.mdt.event.on_season_cont)
            self.mdt.fsm.demand('Race', track, car, self.drivers)
        else:
            self.mdt.fsm.demand('Menu')
