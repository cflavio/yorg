from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.page import Page, PageGui


class CreditPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        txt = OnscreenText(text='', scale=.12, pos=(0, .4),
                           font=menu_gui.font, fg=menu_args.text_fg)
        self.widgets += [txt]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        PageGui.transl_text(self.widgets[0], text)
        PageGui.build_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
