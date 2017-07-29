from random import shuffle
from yyagl.singleton import Singleton
from yyagl.engine.gui.menu import MenuArgs
from yyagl.racing.season.season import SeasonProps


class Utils(object):
    __metaclass__ = Singleton

    @staticmethod
    def get_thanks(num, level):
        names = []
        curr_level = 5
        while len(names) < num or curr_level >= level:
            curr_names = open(eng.curr_path + 'assets/thanks%s.txt' % curr_level).readlines()
            if curr_level >= level:
                names += curr_names
            else:
                shuffle(curr_names)
                names += curr_names[:num - len(names)]
            curr_level -= 1
        shuffle(names)
        return [name.strip() for name in names[:num]]

    @staticmethod
    def get_all_thanks():
        names = []
        for i in range(5, 1, -1):
            tfile = eng.curr_path + 'assets/thanks%s.txt' % i
            names += [name.strip() for name in open(tfile).readlines()]
        return names

    @property
    def menu_args(self):
        return MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), (.75, .25, .25, 1), .1, (-4.6, 4.6, -.32, .88),
            (0, 0, 0, .2), 'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')

    @property
    def drivers(self):
        names = Utils().get_thanks(8, 5)
        drivers = [
            (1, names[0], (4, -2, -2)),
            (2, names[1], (-2, 4, -2)),
            (3, names[2], (0, 4, -4)),
            (4, names[3], (4, -4, 0)),
            (5, names[4], (-2, -2, 4)),
            (6, names[5], (-4, 0, 4)),
            (7, names[6], (4, 0, -4)),
            (8, names[7], (-4, 4, 0))]
        cars = ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea',
                'iperion', '']
        for i, _car in enumerate(cars):
            drivers[i] = drivers[i] + (_car, )
        return drivers

    def season_props(self, car, cars_number, single_race):
        return SeasonProps(
            ['themis', 'kronos', 'diones', 'iapeto', 'phoibe', 'rea', 'iperion'][:int(cars_number)],
            car, self.drivers, 'assets/images/gui/menu_background.jpg',
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            ['desert', 'mountain', 'amusement'],
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .75, 1),
            'assets/sfx/countdown.ogg', single_race)
