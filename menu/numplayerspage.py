from yyagl.lib.gui import Btn, Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class NumPlayersPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def build(self):
        menu_props = self.menu_props
        t_a = menu_props.text_args.copy()
        players_lab = Text(_('How many players?'), pos=(-.2, .6),
                           align='center', **t_a)
        p2_btn = Btn(
            text='2', pos=(-.2, .2), cmd=self.on_btn, extra_args=[2],
            **self.props.gameprops.menu_props.btn_args)
        p3_btn = Btn(
            text='3', pos=(-.2, 0), cmd=self.on_btn, extra_args=[3],
            **self.props.gameprops.menu_props.btn_args)
        p4_btn = Btn(
            text='4', pos=(-.2, -.2), cmd=self.on_btn, extra_args=[4],
            **self.props.gameprops.menu_props.btn_args)
        t_a['scale'] = .06
        widgets = [p2_btn, p3_btn, p4_btn, players_lab]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def on_btn(self, num):
        self.notify('on_nplayers', num)
        self.notify('on_push_page', 'trackpagelocalmp', [self.props])


class NumPlayersPage(Page):
    gui_cls = NumPlayersPageGui

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
