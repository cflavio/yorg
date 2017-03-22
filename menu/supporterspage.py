from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yorg.utils import Utils


class SupportersPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        text = ', '.join(Utils().get_all_thanks())
        txt = OnscreenText(text=text, pos=(0, .6), wordwrap=32,
                           **menu_gui.text_args)
        self.add_widget(txt)
        PageGui.build_page(self)


class SupportersPage(Page):
    gui_cls = SupportersPageGui
