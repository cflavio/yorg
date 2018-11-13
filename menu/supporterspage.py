from yyagl.lib.gui import Text
from yyagl.engine.gui.page import Page
from .thankspage import ThanksPageGui
from yorg.thanksnames import ThanksNames


class SupportersPageGui(ThanksPageGui):

    def build(self, back_btn=True):
        menu_props = self.menu_props
        text = ', '.join(ThanksNames.get_all_thanks())
        txt = Text(text, pos=(-.4, .72), wordwrap=18,
                           **menu_props.text_args)
        self.add_widgets([txt])
        ThanksPageGui.build(self)


class SupportersPage(Page):
    gui_cls = SupportersPageGui
