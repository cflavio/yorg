from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import Menu
from .ingamepage import InGamePage
from yorg.utils import Utils


class InGameMenuGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = Utils().menu_args
        menu_args.background = ''
        menu_args.btn_size = (-8.6, 8.6, -.42, .98)
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(InGamePage(self.menu))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class InGameMenu(GameObjectMdt):
    gui_cls = InGameMenuGui

    def __init__(self, init_lst=[]):
        init_lst = [[('gui', self.gui_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
