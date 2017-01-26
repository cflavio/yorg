from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui


class CreditPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        txt = OnscreenText(text='', pos=(0, .4), **menu_gui.text_args)
        self.widgets += [txt]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        dario = _('Testing')+': Dario Murgia'
        text = '\n\n'.join([flavio, luca, dario])
        self.widgets[0]['text'] = text
        PageGui.build_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
