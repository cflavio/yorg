from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class MultiplayerPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    # def show(self):
    # # then when you go back from the next page, it creates it again
    #     ThanksPageGui.show(self)
    #     self.build()

    def build(self):  # parameters differ from overridden
        omp_cb = lambda: self.notify('on_push_page', 'online',
                                     [self.props])
        menu_data = [
            ('Local', _('Local'), self.__on_local_mp),
            ('Online', _('Online'), omp_cb)]
        widgets = [
            Btn(text=menu[0], pos=(0, .3-i*.28), cmd=menu[2],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def __on_local_mp(self):
        self.notify('on_start_local_mp')
        self.notify('on_push_page', 'localmp', [self.props])


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui

    def __init__(self, mp_props):
        GameObject.__init__(self)
        self.event = self.event_cls(self)
        self.gui = self.gui_cls(self, mp_props)
        # invoke Page's __init__

    def destroy(self):
        self.event.destroy()
        self.gui.destroy()
        GameObject.destroy(self)
