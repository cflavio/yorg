from direct.gui.DirectGuiGlobals import ENTER, EXIT, NORMAL, DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from panda3d.core import TextNode
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject


class MPBtn(GameObject):

    tooltip_align = TextNode.A_right
    tooltip_offset = (.01, 0, -.08)

    def __init__(self, parent, owner, menu_args, img_path, msg_btn_x, cb,
                 usr_name, tooltip):
        GameObject.__init__(self)
        self.owner = owner
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        #lab_args['text_fg'] = menu_args.text_normal
        self.btn = ImgBtn(
            parent=parent, scale=.024, pos=(msg_btn_x, 1, .01),
            frameColor=(1, 1, 1, 1), frameTexture=img_path, command=cb,
            extraArgs=[usr_name], **menu_args.imgbtn_args)
        self.btn.bind(ENTER, self.on_enter)
        self.btn.bind(EXIT, self.on_exit)
        self.tooltip_btn = DirectButton(
            parent=parent, scale=.024, pos=(msg_btn_x, 1, .01),
            frameColor=(1, 1, 1, 0), frameSize=(-1, 1, -1, 1), command=None,
            **menu_args.imgbtn_args)
        self.tooltip_btn.bind(ENTER, self.on_enter)
        self.tooltip_btn.bind(EXIT, self.on_exit)
        self.on_create()
        self.tooltip = DirectLabel(
            text=tooltip, pos=self.btn.get_pos() + self.tooltip_offset,
            parent=parent, text_wordwrap=10, text_bg=(.2, .2, .2, .8),
            text_align=self.tooltip_align, **lab_args)
        self.tooltip.set_bin('gui-popup', 10)
        self.tooltip.hide()

    def on_create(self):
        self.btn.hide()
        self.tooltip_btn.hide()

    def is_hidden(self): return self.btn.is_hidden()

    def show(self):
        if self.btn['state'] == DISABLED:
            self.tooltip_btn.show()
        else:
            self.tooltip_btn.hide()
        return self.btn.show()

    def hide(self):
        self.tooltip_btn.hide()
        return self.btn.hide()

    def enable(self):
        self.tooltip_btn.hide()
        return self.btn.enable()

    def disable(self):
        self.tooltip_btn.show()
        return self.btn.disable()

    def on_enter(self, pos):
        self.owner.on_enter(pos)
        self.tooltip.show()

    def on_exit(self, pos):
        self.owner.on_exit(pos)
        self.tooltip.hide()


class StaticMPBtn(MPBtn):

    tooltip_align = TextNode.A_left
    tooltip_offset = (.01, 0, .05)

    def on_create(self): pass
