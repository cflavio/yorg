from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class AlreadyUsedDlg(GameObject, Subject):

    def __init__(self, menu_args, key, player, cmd):
        Subject.__init__(self)
        GameObject.__init__(self)
        msg = _('The key %s is already used by player %s for %s.' % (
                key, player, cmd))
        self.dialog = OkDialog(
            text=msg,
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
            command=self.on_btn)
        self.eng.log('created dialog ' + self.dialog['text'])

    def on_btn(self, val):
        self.eng.log('already used')
        self.notify('on_already_dlg')

    def destroy(self):
        self.eng.log('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
