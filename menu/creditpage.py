from yyagl.lib.gui import Btn, Text
from yyagl.engine.gui.page import Page
from .thankspage import ThanksPageGui


class CreditPageGui(ThanksPageGui):

    def build(self):
        menu_props = self.menu_props
        dev_str = [_('Code')+': Flavio Calva',
                   _('Art')+': Luca Quartero',
                   _('Audio')+': Jay Bachelor',
                   _('Translations')+': Wuzzy, GunChleoc, Leandro Vergara, xin']
        dev_str = '\n\n'.join(dev_str)
        txt = Text(dev_str, pos=(0, .72), wordwrap=20,
                           **menu_props.text_args)
        btn = Btn(
            text=_('Supporters'), pos=(0, -.4),
            cmd=lambda: self.notify('on_push_page', 'supporters'),
            **menu_props.btn_args)
        self.add_widgets([txt, btn])
        ThanksPageGui.build(self)


class CreditPage(Page):
    gui_cls = CreditPageGui
