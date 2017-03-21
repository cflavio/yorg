from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui


class CreditPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        jay = _('Audio')+': Jay Bachelor'
        dario = _('Testing')+': Dario Murgia'
        text = '\n\n'.join([flavio, luca, jay, dario])
        txt = OnscreenText(text=text, pos=(0, .4), **menu_gui.text_args)
        self.add_widget(txt)
        PageGui.build_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
