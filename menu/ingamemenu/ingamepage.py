from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageGui


class InGamePageGui(PageGui):

    def build_page(self):
        self.frm = DirectFrame(
            frameSize=(-1.5, 1.5, -.9, .9), frameColor=(.95, .95, .7, .85))
        txt = _(
            "What do you want to do?\n\nNB Use 'p' for pausing the game.")
        menu_args = self.menu.gui.menu_args
        self.txt = OnscreenText(
            text=txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=menu_args.text_fg, font=menu_args.font)
        menu_data = [
            ('back to the game', _('back to the game'),
             lambda: self.on_end(True)),
            ('back to the main menu', _('back to the main menu'),
             lambda: self.on_end(False))]
        widgets = [self.frm, self.txt]
        btn_args = self.menu.gui.btn_args
        btn_visit = DirectButton(
            text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2],
            text_scale=.8, **btn_args)
        btn_dont_visit = DirectButton(
            text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2],
            text_scale=.8, **btn_args)
        widgets += [btn_visit, btn_dont_visit]
        map(self.add_widget, widgets)
        PageGui.build_page(self, False)

    def on_end(self, back_to_game):
        if back_to_game:
            self.menu.gui.notify('on_ingame_back')
        else:
            self.menu.gui.notify('on_ingame_exit')


class InGamePage(Page):
    gui_cls = InGamePageGui
