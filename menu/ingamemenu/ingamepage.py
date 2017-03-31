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
        on_back = lambda: self.on_end(True)
        on_end = lambda: self.on_end(False)
        menu_data = [
            ('back to the game', _('back to the game'), on_back),
            ('back to the main menu', _('back to the main menu'), on_end)]
        btn_args = self.menu.gui.btn_args
        btn_visit = DirectButton(
            text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2],
            text_scale=.8, **btn_args)
        btn_dont_visit = DirectButton(
            text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2],
            text_scale=.8, **btn_args)
        map(self.add_widget, [self.frm, self.txt, btn_visit, btn_dont_visit])
        PageGui.build_page(self, False)
        eng.hide_cursor()
        eng.show_standard_cursor()
        eng.do_later(.01, eng.toggle_pause, [False])
        # in the next frame since otherwise InGameMenu will be paused while
        # waiting page's creation, and when it is restored it is destroyed,
        # then the creation callback finds a None menu

    def on_end(self, back_to_game):
        eng.hide_standard_cursor()
        self.menu.gui.notify('on_ingame_' + ('back' if back_to_game else 'exit'))
        eng.do_later(.01, eng.toggle_pause)


class InGamePage(Page):
    gui_cls = InGamePageGui
