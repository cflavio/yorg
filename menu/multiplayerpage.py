from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageGui
from .serverpage import ServerPage
from .clientpage import ClientPage


class MultiplayerPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        menu_data = [
            ('Server',
             lambda: self.menu.logic.push_page(ServerPage(self.menu))),
            ('Client',
             lambda: self.menu.logic.push_page(ClientPage(self.menu)))]
        widgets = [
            DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                         **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        map(self.add_widget, widgets)
        PageGui.build_page(self)


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui
