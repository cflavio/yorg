'''This is the main page of the menu.'''
from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.page import PageGui
from .singleplayerpage import SingleplayerPage
from .multiplayerpage import MultiplayerPage
from .optionpage import OptionPage
from .creditpage import CreditPage


class YorgMainPageGui(MainPageGui):
    '''This is the GUI of the main page.'''

    def build(self):
        menu_data = [
            ('Single Player', _('Single Player'),
             lambda: self.menu.logic.push_page(SingleplayerPage(self.menu))),
            ('Multiplayer', _('Multiplayer'),
             lambda: self.menu.logic.push_page(MultiplayerPage(self.menu))),
            ('Options', _('Options'),
             lambda: self.menu.logic.push_page(OptionPage(self.menu))),
            ('Credits', _('Credits'),
             lambda: self.menu.logic.push_page(CreditPage(self.menu))),
            ('Quit', _('Quit'),
             lambda: messenger.send('window-closed'))]
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.widgets += [
            DirectButton(
                text='', scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[2], frameSize=menu_args.btn_size,
                rolloverSound=menu_gui.rollover,
                clickSound=menu_gui.click)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(self.widgets):
            PageGui.transl_text(wdg, menu_data[i][0])
        MainPageGui.build(self)


class YorgMainPage(MainPage):
    '''This class models a page.'''
    gui_cls = YorgMainPageGui
