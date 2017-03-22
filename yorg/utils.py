from random import shuffle
from yyagl.singleton import Singleton
from yyagl.engine.gui.menu import MenuArgs


@Singleton
class Utils(object):

    @staticmethod
    def get_thanks(num):
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        return names[:num + 1]

    @property
    def menu_args(self):
        return MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .75, 1), .1, (-4.6, 4.6, -.32, .88), (0, 0, 0, .2),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png', (.75, .25, .25, 1))