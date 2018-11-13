from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class RoomPageGui(ThanksPageGui):

    def __init__(self, mediator, menu_props):
        self.menu_props = menu_props
        ThanksPageGui.__init__(self, mediator, menu_props)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        widgets = []
        self.add_widgets(widgets)
        ThanksPageGui.build(self)


class RoomPage(Page):
    gui_cls = RoomPageGui

    def __init__(self, menu_props, room, nick):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, menu_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
