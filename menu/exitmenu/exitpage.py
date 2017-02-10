from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectButton import DirectButton
import sys


class ExitPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui

        self.frm = DirectFrame(frameSize=(-1.5, 1.5, -.9, .9), frameColor=(.95, .95, .7, .85))
        txt = _(
            'Please, visit our site after exiting!\n\nIt helps us! Thank you!')
        self.txt = OnscreenText(text=txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=(.75, .75, .25, 1), font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'))
        menu_data = [
            ('visit our site after exiting', _('visit our site after exiting'),
             lambda: self.on_end(True)),
            ("don't visit our site after exiting", _("don't visit our site after exiting"),
             lambda: self.on_end(False))]
        self.widgets = [self.frm, self.txt]
        btn_args = {
            'text_font': eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'),
            'text_fg': (.75, .75, .25, 1),
            'frameColor': (0, 0, 0, .2),
            'relief': FLAT,
            'frameSize': (-1, 1, -.18, .19),
            'rolloverSound': loader.loadSfx('assets/sfx/menu_over.wav'),
            'clickSound': loader.loadSfx('assets/sfx/menu_clicked.ogg')}
        btn_visit = DirectButton(text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2], text_scale=.12, **btn_args)
        btn_dont_visit = DirectButton(text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2], text_scale=.08, **btn_args)
        self.widgets += [btn_visit, btn_dont_visit]
        PageGui.build_page(self, False)

    def on_end(self, visit):
        if visit:
            eng.gui.open_browser('http://www.ya2.it')
        sys.exit()


class ExitPage(Page):
    gui_cls = ExitPageGui
