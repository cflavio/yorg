from sys import exit as sys_exit
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageGui


class ExitPageGui(PageGui):

    def bld_page(self):
        menu_args = self.mdt.menu.gui.menu_args
        self.frm = DirectFrame(
            frameSize=(-1.5, 1.5, -.9, .9), frameColor=(.95, .95, .7, .85))
        txt = _(
            'Please, visit our site after exiting!\n\nIt helps us! Thank you!')
        self.txt = OnscreenText(
            text=txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=menu_args.text_fg, font=menu_args.font)
        menu_data = [
            ('visit our site after exiting', _('visit our site after exiting'),
             lambda: self.on_end(True)),
            ("don't visit our site after exiting",
             _("don't visit our site after exiting"),
             lambda: self.on_end(False))]
        btn_args = self.mdt.menu.gui.menu_args.btn_args
        btn_args['frameSize'] = (-12, 12, -.8, 1.2)
        btn_visit = DirectButton(
            text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2],
            text_scale=.9, **btn_args)
        btn_dont_visit = DirectButton(
            text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2],
            text_scale=.7, **btn_args)
        widgets = [self.frm, self.txt, btn_visit, btn_dont_visit]
        map(self.add_widget, widgets)
        PageGui.bld_page(self, False)

    @staticmethod
    def on_end(visit):
        if visit:
            eng.open_browser('http://www.ya2.it')
        eng.do_later(.5, sys_exit)


class ExitPage(Page):
    gui_cls = ExitPageGui
