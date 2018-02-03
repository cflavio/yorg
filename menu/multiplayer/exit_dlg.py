from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject


class ExitDialog(Subject):

    def __init__(self, menu_args, msg):
        Subject.__init__(self)
        self.user = str(msg['muc']['nick'])
        self.msg = msg
        self.dialog = OkDialog(
            text=_('the server user %s has quitted') % self.user,
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

    def on_btn(self, val):
        self.notify('on_exit_dlg')

    def destroy(self):
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
