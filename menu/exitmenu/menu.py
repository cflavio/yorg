from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import MenuArgs, Menu
from .exitpage import ExitPage


class _Gui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1),
            (.75, .75, .25, 1), .1, (-4.6, 4.6, -.32, .88), (0, 0, 0, .2), '',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg', '',
            (.75, .25, .25, 1))
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(ExitPage(self.menu))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class ExitMenu(GameObjectMdt):
    gui_cls = _Gui

    def __init__(self, init_lst=[]):
        init_lst = [[('gui', self.gui_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
