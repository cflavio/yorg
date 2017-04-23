from yyagl.gameobject import GameObject, Gui
from yyagl.engine.gui.menu import Menu
from .exitpage import ExitPage


class ExitMenuGui(Gui):

    def __init__(self, mdt, menu_args):
        Gui.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.push_page(ExitPage(self.menu))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class ExitMenu(GameObject):

    def __init__(self, menu_args):
        init_lst = [[('gui', ExitMenuGui, [self, menu_args])]]
        GameObject.__init__(self, init_lst)
