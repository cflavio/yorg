from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page
from .thankspage import ThanksPageGui
from yorg.thanksnames import ThanksNames


class SupportersPageGui(ThanksPageGui):

    def build(self, back_btn=True):
        menu_args = self.menu_args
        text = ', '.join(ThanksNames.get_all_thanks())
        txt = OnscreenText(text=text, pos=(-.2, .72), wordwrap=16,
                           **menu_args.text_args)
        self.add_widgets([txt])
        ThanksPageGui.build(self)


class SupportersPage(Page):
    gui_cls = SupportersPageGui
