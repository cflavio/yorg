from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from .forms import UserFrm


class MatchFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.invited_users = []
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = menu_args.text_bg
        self.match_lab = DirectLabel(
            text=_('Current match'), pos=(-.85, 1, .93), hpr=(0, 0, -90),
            parent=base.a2dBottomRight, text_align=TextNode.A_right,
            **lab_args)
        self.match_frm = DirectFrame(
            frameSize=(-.02, .8, 0, .45),
            frameColor=(.2, .2, .2, .5),
            pos=(-.82, 1, .49), parent=base.a2dBottomRight)
        btn_args = self.menu_args.btn_args
        btn_args['scale'] = .06
        DirectButton(text=_('Start'), pos=(.39, 1, .03), command=self.on_start,
                     parent=self.match_frm, **btn_args)

    @staticmethod
    def trunc(name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_invite(self, usr):
        idx = len(self.invited_users)
        x = .02 + .4 * (idx / 4)
        y = .38 - .08 * (idx % 4)
        UserFrm(self.trunc(usr.name, 8), usr, usr.is_supporter, (x, 1, y),
                self.match_frm, self.menu_args, .32)
        self.invited_users += [usr.name]

    def on_start(self): print 'start'
