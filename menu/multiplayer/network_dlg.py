from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class NetworkDialog(GameObject, Subject):

    def __init__(self, menu_args):
        Subject.__init__(self)
        GameObject.__init__(self)
        net_msg = _(
            'Connection error. Please check that your router is configured '
            'for doing port-forwarding for port 9099 on your host and your '
            'firewall allows traffic for Yorg on port 9099.')
        self.dialog = OkDialog(
            text=net_msg,
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
        self.eng.log('exit button')
        self.notify('on_network_dlg')

    def destroy(self):
        self.eng.log('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
