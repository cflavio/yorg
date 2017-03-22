from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import Menu
from .exitpage import ExitPage


class ExitMenuGui(Gui):

    def __init__(self, mdt, menu_args):
        Gui.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(ExitPage(self.menu))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class ExitMenu(GameObjectMdt):

    def __init__(self, menu_args):
        init_lst = [[('gui', ExitMenuGui, [self, menu_args])]]
        GameObjectMdt.__init__(self, init_lst)
