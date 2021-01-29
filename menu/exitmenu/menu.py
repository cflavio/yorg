from yyagl.gameobject import GameObject, GuiColleague
from yyagl.engine.gui.menu import Menu
from .exitpage import ExitPage


class ExitMenuGui(GuiColleague):

    def __init__(self, mediator, menu_props):
        GuiColleague.__init__(self, mediator)
        self.menu = Menu(menu_props)
        self.menu.push_page(ExitPage(menu_props))

    def destroy(self):
        self.menu = self.menu.destroy()
        GuiColleague.destroy(self)


class ExitMenu(GameObject):

    def __init__(self, menu_props):
        GameObject.__init__(self)
        self.gui = ExitMenuGui(self, menu_props)
