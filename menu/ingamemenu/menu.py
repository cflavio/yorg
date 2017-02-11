from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import MenuArgs, Menu
from .ingamepage import InGamePage


class _Gui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/Hanken-Book.ttf', (.75, .75, .25, 1), .1,
            (-4.6, 4.6, -.32, .88), (0, 0, 0, .2), (.9, .9, .9, .8),
            '',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            '')
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(InGamePage(self.menu))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class InGameMenu(GameObjectMdt):
    gui_cls = _Gui


    def __init__(self, init_lst=[]):
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)
