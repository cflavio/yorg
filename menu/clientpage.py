from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class ClientPageGui(ThanksPageGui):

    def __init__(self, mediator, menu_props):
        self.menu_props = menu_props
        ThanksPageGui.__init__(self, mediator, menu_props.gameprops.menu_props)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        widgets = []
        self.add_widgets(widgets)
        ThanksPageGui.build(self)


class ClientPage(Page):
    gui_cls = ClientPageGui

    def __init__(self, menu_props):
        self.menu_props = menu_props
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.menu_props])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)
