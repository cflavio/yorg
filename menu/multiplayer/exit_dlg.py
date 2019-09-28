from logging import info
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class ExitDialog(GameObject, Subject):

    def __init__(self, menu_props, uid):
        Subject.__init__(self)
        GameObject.__init__(self)
        self.user = uid
        self.dialog = OkDialog(
            text=_('the server user %s has quit') % self.user,
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
            command=self.on_btn)
        info('created dialog ' + self.dialog['text'])

    def on_btn(self, val):
        self.eng.client.register_rpc('leave_curr_room')
        self.eng.client.leave_curr_room()
        info('exit button')
        self.notify('on_exit_dlg')

    def destroy(self):
        info('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
