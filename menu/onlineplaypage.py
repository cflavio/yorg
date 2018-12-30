from time import strftime
from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class OnlinePlayPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        ccb = lambda: self.notify('on_push_page', 'client', [self.props])
        menu_data = [
            ('Host', self.on_server),
            ('Join', ccb)]
        widgets = [
            Btn(text=menu[0], pos=(-.2, .3-i*.28), cmd=menu[1],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def on_server(self):
        time_code = strftime('%y%m%d%H%M%S')
        roomname = self.eng.client.myid + time_code
        self.notify('on_create_room', roomname, self.eng.client.myid)


class OnlinePlayPage(Page):
    gui_cls = OnlinePlayPageGui

    def __init__(self, mp_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, mp_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
