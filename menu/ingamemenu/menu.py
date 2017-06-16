from yyagl.gameobject import GameObject, Gui
from yyagl.engine.gui.menu import Menu
from yorg.utils import Utils
from .ingamepage import InGamePage


class InGameMenuGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = Utils().menu_args
        menu_args.background_img = ''
        menu_args.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_args)
        self.menu.push_page(InGamePage(menu_args, self.menu))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class InGameMenu(GameObject):
    gui_cls = InGameMenuGui

    def __init__(self, init_lst=[]):
        init_lst = [[('gui', self.gui_cls, [self])]]
        GameObject.__init__(self, init_lst)
