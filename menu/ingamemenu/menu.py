from copy import deepcopy
from yyagl.gameobject import GameObject, GuiColleague
from yyagl.engine.gui.menu import Menu
from .ingamepage import InGamePage


class InGameMenuGui(GuiColleague):

    def __init__(self, mediator, menu_props, keys, season_kind):
        GuiColleague.__init__(self, mediator)
        menu_props_c = deepcopy(menu_props)
        menu_props_c.background_img_path = ''
        menu_props_c.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_props_c)
        page = InGamePage.init_cls(season_kind)(menu_props_c, keys)
        page.gui.attach(self.on_ingame_back)
        page.gui.attach(self.on_ingame_exit)
        self.menu.push_page(page)

    def on_ingame_back(self):
        self.notify('on_ingame_back')

    def on_ingame_exit(self):
        self.notify('on_ingame_exit')

    def destroy(self):
        self.menu = self.menu.destroy()
        GuiColleague.destroy(self)


class InGameMenu(GameObject):
    gui_cls = InGameMenuGui

    def __init__(self, menu_props, keys, season_kind):
        GameObject.__init__(self)
        self.gui = self.gui_cls(self, menu_props, keys, season_kind)

    def destroy(self):
        self.gui.destroy()
        GameObject.destroy(self)
