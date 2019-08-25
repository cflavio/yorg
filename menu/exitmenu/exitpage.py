from sys import exit as sys_exit
from direct.gui.OnscreenText import OnscreenText
from yyagl.lib.gui import Btn, Frame, Text
from yyagl.engine.gui.page import Page, PageGui


class ExitPageGui(PageGui):

    def build(self, back_btn=True):
        menu_props = self.menu_props
        frm = Frame(
            frame_size=(-1.5, 1.5, -.9, .9), frame_col=(.95, .95, .7, .85))
        txt = _(
            'Please, visit our site after exiting!\n\nIt helps us! Thank you!')
        txt = Text(
            txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=menu_props.text_active_col, font=menu_props.font)
        menu_data = [
            ('visit our site after exiting', _('visit our site after exiting'),
             lambda: self.on_end(True)),
            ("don't visit our site after exiting",
             _("don't visit our site after exiting"),
             lambda: self.on_end(False))]
        btn_args = self.menu_props.btn_args
        btn_args['frame_size'] = (-12, 12, -.8, 1.2)
        btn_visit = Btn(
            text=menu_data[0][1], pos=(0, 0), cmd=menu_data[0][2],
            text_scale=.9, **btn_args)
        btn_dont_visit = Btn(
            text=menu_data[1][1], pos=(0, -.5), cmd=menu_data[1][2],
            text_scale=.7, **btn_args)
        widgets = [frm, txt, btn_visit, btn_dont_visit]
        self.add_widgets(widgets)
        PageGui.build(self, False)

    @staticmethod
    def on_end(visit):
        if visit:
            ExitPageGui.eng.open_browser('https://www.ya2.it')
        #ExitPageGui.eng.xmpp.destroy()
        ExitPageGui.eng.do_later(.5, sys_exit)


class ExitPage(Page):
    gui_cls = ExitPageGui
