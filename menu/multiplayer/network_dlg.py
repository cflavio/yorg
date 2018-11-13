from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.observer import Subject
from yyagl.gameobject import GameObject


class NetworkDialog(GameObject, Subject):

    def __init__(self, menu_props):
        Subject.__init__(self)
        GameObject.__init__(self)
        net_msg = _(
            'Connection error. Please check that (i) your firewall allows '
            'traffic for Yorg on port 9099 and (ii) the server user has '
            'opened her port 9099 (here is a guide for checking it: '
            'http://www.ya2.it/pages/check-your-ports.html).')
        self.dialog = OkDialog(
            text=net_msg,
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
        self.eng.log('created dialog ' + self.dialog['text'])

    def on_btn(self, val):
        self.eng.log('exit button')
        self.notify('on_network_dlg')

    def destroy(self):
        self.eng.log('destroyed dialog ' + self.dialog['text'])
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)
