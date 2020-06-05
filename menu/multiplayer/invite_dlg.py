from logging import info
from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class InviteDialog(GameObject, Subject):

    def __init__(self, menu_props, from_, roomname):
        Subject.__init__(self)
        GameObject.__init__(self)
        self.from_ = from_
        self.roomname = roomname
        self.dialog = YesNoDialog(
            base.a2dBottomLeft,
            text=_('%s has invited you to a match, do you agree?') % from_,
            text_wordwrap=16,
            text_fg=menu_props.text_active_col,
            text_font=menu_props.font,
            pad=(.03, .03),
            topPad=0,
            midPad=.01,
            relief=FLAT,
            frameColor=(.8, .8, .8, .9),
            button_relief=FLAT,
            button_frameColor=(.2, .2, .2, .2),
            button_text_fg=menu_props.text_active_col,
            button_text_font=menu_props.font,
            buttonValueList=['yes', 'no'],
            command=self.on_btn)
        size = self.dialog['frameSize']
        self.dialog.set_pos(-size[0] + .05, 1, -size[2] + .05)
        info('created dialog ' + self.dialog['text'])

    def on_btn(self, val):
        info('invite button ' + val)
        self.notify('on_invite_answer', self.from_, self.roomname,
                    val == 'yes')

    def destroy(self):
        info('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
