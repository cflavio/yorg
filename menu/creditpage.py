from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page
from .thankspage import ThanksPageGui


class CreditPageGui(ThanksPageGui):

    def bld_page(self):
        menu_args = self.menu_args
        dev_str = [_('Code')+': Flavio Calva',
                   _('Art')+': Luca Quartero',
                   _('Audio')+': Jay Bachelor',
                   _('Translations')+': Wuzzy, GunChleoc, Leandro Vergara']
        dev_str = '\n\n'.join(dev_str)
        txt = OnscreenText(text=dev_str, pos=(-.2, .72), wordwrap=20,
                           **menu_args.text_args)
        btn = DirectButton(
            text=_('Supporters'), pos=(-.2, 1, -.4),
            command=lambda: self.notify('on_push_page', 'supporters'),
            **menu_args.btn_args)
        map(self.add_widget, [txt, btn])
        ThanksPageGui.bld_page(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
