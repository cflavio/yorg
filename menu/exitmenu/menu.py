from yyagl.gameobject import GameObject, GuiColleague
from yyagl.engine.gui.menu import Menu
from .exitpage import ExitPage


class ExitMenuGui(GuiColleague):

    def __init__(self, mdt, menu_args):
        GuiColleague.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.push_page(ExitPage(menu_args))

    def destroy(self):
        self.menu = self.menu.destroy()
        GuiColleague.destroy(self)


class ExitMenu(GameObject):

    def __init__(self, menu_args):
        init_lst = [[('gui', ExitMenuGui, [self, menu_args])]]
        GameObject.__init__(self, init_lst)
