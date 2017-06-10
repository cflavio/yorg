from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yorg.utils import Utils


class SupportersPageGui(PageGui):

    def bld_page(self):
        menu_args = self.menu_args
        text = ', '.join(Utils().get_all_thanks())
        txt = OnscreenText(text=text, pos=(0, .6), wordwrap=32,
                           **menu_args.text_args)
        self.add_widget(txt)
        PageGui.bld_page(self)


class SupportersPage(Page):
    gui_cls = SupportersPageGui
