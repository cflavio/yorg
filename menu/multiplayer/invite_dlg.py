from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class InviteDialog(GameObject, Subject):

    def __init__(self, menu_args, from_, roomname):
        Subject.__init__(self)
        GameObject.__init__(self)
        self.from_ = from_
        self.roomname = roomname
        self.dialog = YesNoDialog(
            base.a2dBottomLeft,
            text=_('%s has invited you to a match, do you agree?') % from_,
            text_wordwrap=16,
            text_fg=menu_args.text_active,
            text_font=menu_args.font,
            pad=(.03, .03),
            topPad=0,
            midPad=.01,
            relief=FLAT,
            frameColor=(.8, .8, .8, .9),
            button_relief=FLAT,
            button_frameColor=(.2, .2, .2, .2),
            button_text_fg=menu_args.text_active,
            button_text_font=menu_args.font,
            buttonValueList=['yes', 'no'],
            command=self.on_btn)
        size = self.dialog['frameSize']
        self.dialog.set_pos(-size[0] + .05, 1, -size[2] + .05)
        self.eng.log('created dialog ' + self.dialog['text'])

    def on_btn(self, val):
        self.eng.log('invite button ' + val)
        self.notify('on_invite_answer', self.from_, self.roomname, val == 'yes')

    def destroy(self):
        self.eng.log('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
