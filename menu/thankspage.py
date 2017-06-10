from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from yorg.utils import Utils
from yyagl.engine.gui.page import PageGui


class ThanksPageGui(PageGui):

    def bld_page(self):
        menu_args = self.menu_args
        t_a = menu_args.text_args
        t_a['fg'] = menu_args.text_bg
        t_a['scale'] = .06
        self.add_widget(OnscreenText(
            text=_('Thanks to: ') + Utils().get_thanks(1)[0], pos=(.05, .05),
            align=TextNode.A_left, parent=base.a2dBottomLeft, **t_a))
        PageGui.bld_page(self)
