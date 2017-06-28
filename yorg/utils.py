from random import shuffle
from yyagl.singleton import Singleton
from yyagl.engine.gui.menu import MenuArgs
from yyagl.racing.season.season import SeasonProps


class Utils(object):
    __metaclass__ = Singleton

    @staticmethod
    def get_thanks(num):
        names = open(eng.curr_path + 'assets/thanks.txt').readlines()
        shuffle(names)
        return [name.strip() for name in names[:num]]

    @staticmethod
    def get_all_thanks():
        tfile = eng.curr_path + 'assets/thanks.txt'
        return [name.strip() for name in open(tfile).readlines()]

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
        names = Utils().get_thanks(8)
        drivers = [
            (1, names[0], (4, -2, -2)),
            (2, names[1], (-2, 4, -2)),
            (3, names[2], (0, 4, -4)),
            (4, names[3], (4, -4, 0)),
            (5, names[4], (-2, -2, 4)),
            (6, names[5], (-4, 0, 4)),
            (7, names[6], (4, 0, -4)),
            (8, names[7], (-4, 4, 0))]
        cars = ['kronos', 'themis', 'diones', 'iapeto', 'phoibe', 'rea',
                'iperion', '']
        for i, _car in enumerate(cars):
            drivers[i] = drivers[i] + (_car, )
        return drivers

    def season_props(self, car):
        return SeasonProps(
            ['kronos', 'themis', 'diones', 'iapeto', 'phoibe', 'rea', 'iperion'],
            car, self.drivers, 'assets/images/gui/menu_background.jpg',
            ['assets/images/tuning/engine.png',
             'assets/images/tuning/tires.png',
             'assets/images/tuning/suspensions.png'],
            ['prototype', 'desert', 'mountain', 'amusement'],
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .75, 1))
