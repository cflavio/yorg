from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.page import Page, PageGui
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
        self.widgets = [
            DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                         **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        PageGui.build_page(self)


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'MultiplayerPageGui', [self.menu])],
            [(self.build_logic, 'Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'PageEvent')]]
