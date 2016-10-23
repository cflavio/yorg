from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.page import Page, PageGui


class CreditPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        txt = OnscreenText(text='', scale=.12, pos=(0, .4),
                           font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        PageGui.transl_text(self.widgets[0], text)
        PageGui.build(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
