from panda3d.core import TextNode
from yyagl.library.gui import Text
from yorg.thanksnames import ThanksNames
from yyagl.engine.gui.page import PageGui


class ThanksPageGui(PageGui):

    def build(self, back_btn=True):
        menu_args = self.menu_args
        t_a = menu_args.text_args
        t_a['fg'] = menu_args.text_normal
        t_a['scale'] = .06
        thanks_txt = Text(
            _('Thanks to: ') + ThanksNames.get_thanks(1, 3)[0],
            pos=(.05, .05), align=TextNode.A_left, parent='bottomleft',
            wordwrap=64, **t_a)
        self.add_widgets([thanks_txt])
        PageGui.build(self)
