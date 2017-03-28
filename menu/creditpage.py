from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page
from .supporterspage import SupportersPage
from .thankspage import ThanksPageGui


class CreditPageGui(ThanksPageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        jay = _('Audio')+': Jay Bachelor'
        dario = _('Testing')+': Dario Murgia'
        text = '\n\n'.join([flavio, luca, jay, dario])
        txt = OnscreenText(text=text, pos=(0, .64), **menu_gui.text_args)
        btn = DirectButton(
            text=_('Supporters'), pos=(0, 1, -.4),
            command=lambda: self.menu.push_page(SupportersPage(self.menu)),
            **menu_gui.btn_args)
        map(self.add_widget, [txt, btn])
        ThanksPageGui.build_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
