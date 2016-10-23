from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.page import Page, PageGui
from .serverpage import ServerPage
from .clientpage import ClientPage


class MultiplayerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        menu_data = [
            ('Server',
             lambda: self.menu.logic.push_page(ServerPage(self.menu))),
            ('Client',
             lambda: self.menu.logic.push_page(ClientPage(self.menu)))]
        self.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        PageGui.build(self)


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui
