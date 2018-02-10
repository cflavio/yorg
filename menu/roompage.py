from yyagl.library.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class RoomPageGui(ThanksPageGui):

    def __init__(self, mediator, menu_args):
        self.menu_args = menu_args
        ThanksPageGui.__init__(self, mediator, menu_args)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        widgets = []
        self.add_widgets(widgets)
        ThanksPageGui.build(self)


class RoomPage(Page):
    gui_cls = RoomPageGui

    def __init__(self, menu_args, room, nick):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, menu_args])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
