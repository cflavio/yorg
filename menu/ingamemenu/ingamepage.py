from yyagl.lib.gui import Btn, Frame, Text
from yyagl.engine.gui.page import Page, PageGui, PageFacade


class InGamePageGuiMultiplayer(PageGui):

    def __init__(self, mediator, menu_props, keys):
        self.keys = keys
        PageGui.__init__(self, mediator, menu_props)

    def build(self, back_btn=True):  # parameters differ from overridden
        frm = Frame(
            frame_size=(-1.5, 1.5, -.9, .9), frame_col=(.95, .95, .7, .85))
        question_txt = _(
            "What do you want to do?\n\nNote: use '%s' for pausing the game.")
        question_txt = question_txt % self.keys.pause
        menu_props = self.menu_props
        txt = Text(
            question_txt, pos=(0, .64), scale=.08, wordwrap=32,
            fg=menu_props.text_active_col, font=menu_props.font)
        on_back = lambda: self.on_end(True)
        on_end = lambda: self.on_end(False)
        menu_data = [
            ('back to the game', _('back to the game'), on_back),
            ('back to the main menu', _('back to the main menu'), on_end)]
        btn_args = menu_props.btn_args
        btn_visit = Btn(
            text=menu_data[0][1], pos=(0, 0), cmd=menu_data[0][2],
            text_scale=.8, **btn_args)
        btn_dont_visit = Btn(
            text=menu_data[1][1], pos=(0, -.5), cmd=menu_data[1][2],
            text_scale=.8, **btn_args)
        self.add_widgets([frm, txt, btn_visit, btn_dont_visit])
        PageGui.build(self, False)
        self.eng.show_cursor()

    def on_end(self, back_to_game):
        self.eng.hide_standard_cursor()
        evt_name = 'back' if back_to_game else 'exit'
        if self.eng.server.is_active and not back_to_game:
            self.eng.client.send(['end_race'])
        self.notify('on_ingame_' + evt_name)


class InGamePageGui(InGamePageGuiMultiplayer):

    def build(self, back_btn=True):
        InGamePageGuiMultiplayer.build(self, back_btn)
        if not self.eng.pause.paused:
            self.eng.do_later(.01, self.eng.toggle_pause, [False])
        # in the next frame since otherwise InGameMenu will be paused while
        # waiting page's creation, and when it is restored it is destroyed,
        # then the creation callback finds a None menu

    def on_end(self, back_to_game):
        InGamePageGuiMultiplayer.on_end(self, back_to_game)
        if self.eng.pause.paused:
            self.eng.do_later(.01, self.eng.toggle_pause)


class InGamePageMultiplayer(Page, PageFacade):
    gui_cls = InGamePageGuiMultiplayer

    def __init__(self, menu_props, keys):
        self.keys = keys
        self.menu_props = menu_props
        PageFacade.__init__(self)
        Page.__init__(self, menu_props)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.menu_props, self.keys)


class InGamePage(InGamePageMultiplayer):
    gui_cls = InGamePageGui

    @staticmethod
    def init_cls():
        multip = InGamePage.eng.server.is_active or InGamePage.eng.client.is_active
        return InGamePageMultiplayer if multip else InGamePage
