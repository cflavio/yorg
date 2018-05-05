from copy import deepcopy
from yyagl.gameobject import GameObject, GuiColleague
from yyagl.engine.gui.menu import Menu
from .ingamepage import InGamePage


class InGameMenuGui(GuiColleague):

    def __init__(self, mediator, menu_args, keys):
        GuiColleague.__init__(self, mediator)
        menu_args_c = deepcopy(menu_args)
        menu_args_c.background_img = ''
        menu_args_c.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_args_c)
        page = InGamePage.init_cls()(menu_args_c, keys)
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

    def __init__(self, menu_args, keys):
        init_lst = [[('gui', self.gui_cls, [self, menu_args, keys])]]
        GameObject.__init__(self, init_lst)
