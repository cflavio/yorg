from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.page import Page, PageEvent, PageGui


class CreditPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.widgets += [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=menu_gui.font, fg=(.75, .75, .75, 1))]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        PageGui.transl_text(self.widgets[0], text)
        PageGui.build(self)


class CreditPage(Page):
    '''This class models a page.'''
    gui_cls = CreditPageGui
