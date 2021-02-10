from panda3d.core import TextNode
from yyagl.lib.gui import Text
from yyagl.engine.gui.page import PageGui
from yorg.thanksnames import ThanksNames


class ThanksPageGui(PageGui):

    def build(self, back_btn=True, exit_behav=False):
        menu_props = self.menu_props
        t_a = menu_props.text_args
        t_a['fg'] = menu_props.text_normal_col
        t_a['scale'] = .06
        thanks_txt = Text(
            _('Thanks to: ') + ThanksNames.get_thanks(1, 3)[0],
            pos=(.05, .05), align=TextNode.A_left, parent='bottomleft',
            wordwrap=64, **t_a)
        self.add_widgets([thanks_txt])
        PageGui.build(self, back_btn, exit_behav)
