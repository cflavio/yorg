from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectButton import DirectButton


class InGamePageGui(PageGui):

    def build_page(self):
        self.frm = DirectFrame(
            frameSize=(-1.5, 1.5, -.9, .9), frameColor=(.95, .95, .7, .85))
        txt = _(
            "What do you want to do?\n\nNB Use 'p' for pausing the game.")
        self.txt = OnscreenText(text=txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=(.75, .75, .25, 1),
            font=eng.font_mgr.load_font('assets/fonts/Hanken-Book.ttf'))
        menu_data = [
            ('back to the game', _('back to the game'),
             lambda: self.on_end(True)),
            ('back to the main menu', _('back to the main menu'),
             lambda: self.on_end(False))]
        self.widgets = [self.frm, self.txt]
        font_path = 'assets/fonts/Hanken-Book.ttf'
        btn_args = {
            'text_font': eng.font_mgr.load_font(font_path),
            'text_fg': (.75, .75, .25, 1),
            'frameColor': (0, 0, 0, .2),
            'relief': FLAT,
            'frameSize': (-1, 1, -.18, .19),
            'rolloverSound': loader.loadSfx('assets/sfx/menu_over.wav'),
            'clickSound': loader.loadSfx('assets/sfx/menu_clicked.ogg')}
        btn_visit = DirectButton(
            text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2],
            text_scale=.12, **btn_args)
        btn_dont_visit = DirectButton(
            text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2],
            text_scale=.12, **btn_args)
        self.widgets += [btn_visit, btn_dont_visit]
        PageGui.build_page(self, False)

    def on_end(self, back_to_game):
        if back_to_game:
            game.fsm.race.event.register_menu()
            eng.gui.cursor.hide()
            self.mdt.destroy()
        else:
            if game.fsm.race.fsm.getCurrentOrNextState() != 'Results':
                game.fsm.race.logic.exit_play()
            game.fsm.demand('Menu')
            self.mdt.destroy()


class InGamePage(Page):
    gui_cls = InGamePageGui
