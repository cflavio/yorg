from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page
from .supporterspage import SupportersPage
from .thankspage import ThanksPageGui


class CreditPageGui(ThanksPageGui):

    def bld_page(self):
        menu_args = self.menu_args
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        jay = _('Audio')+': Jay Bachelor'
        dario = _('Testing')+': Dario Murgia'
        text = '\n\n'.join([flavio, luca, jay, dario])
        txt = OnscreenText(text=text, pos=(0, .64), **menu_args.text_args)
        btn = DirectButton(
            text=_('Supporters'), pos=(0, 1, -.4),
            # command=lambda: self.menu.push_page(SupportersPage(self.menu_args)),
            command=lambda: self.notify('on_push_page', SupportersPage(
                self.menu_args, self.mdt.menu)),
            **menu_args.btn_args)
        map(self.add_widget, [txt, btn])
        ThanksPageGui.bld_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
