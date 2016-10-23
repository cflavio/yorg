from racing.game.gameobject.gameobject import GameObjectMdt, Gui
from racing.game.engine.gui.menu import MenuArgs, Menu
from .mainpage import YorgMainPage


class _Gui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/zekton rg.ttf', (.75, .75, .75, 1), .12,
            (-3, 3, -.32, .88), (0, 0, 0, .2), (.9, .9, .9, .8),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(YorgMainPage(self.menu))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class YorgMenu(GameObjectMdt):
    gui_cls = _Gui
