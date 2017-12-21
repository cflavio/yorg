from sleekxmpp.jid import JID
from direct.gui.DirectGuiGlobals import ENTER, EXIT
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from yyagl.engine.gui.imgbtn import ImgBtn


class UserFrm:

    def __init__(self, name, pos, parent, menu_args):
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        self.frm = DirectButton(
            frameSize=(-.01, .59, .05, -.03), frameColor=(1, 1, 1, 0),
            pos=pos, parent=parent)
        self.frm.bind(ENTER, self.on_enter)
        self.frm.bind(EXIT, self.on_exit)
        self.lab = DirectLabel(text=name, pos=(0, 1, 0), parent=self.frm,
                               text_align=TextNode.A_left, **lab_args)
        self.lab.bind(ENTER, self.on_enter)
        self.lab.bind(EXIT, self.on_exit)
        self.invite_btn = ImgBtn(
                parent=self.frm,
                scale=.024,
                pos=(.56, 1, .01),
                frameColor=(1, 1, 1, 1),
                frameTexture='assets/images/gui/invite.txo',
                command=self.on_invite,
                extraArgs=[name],
                **menu_args.imgbtn_args)
        self.invite_btn.bind(ENTER, self.on_enter)
        self.invite_btn.bind(EXIT, self.on_exit)
        self.invite_btn.hide()
        self.msg_btn = ImgBtn(
                parent=self.frm,
                scale=.024,
                pos=(.5, 1, .01),
                frameColor=(1, 1, 1, 1),
                frameTexture='assets/images/gui/message.txo',
                command=self.on_msg,
                extraArgs=[name],
                **menu_args.imgbtn_args)
        self.msg_btn.bind(ENTER, self.on_enter)
        self.msg_btn.bind(EXIT, self.on_exit)
        self.msg_btn.hide()

    def on_invite(self, usr):
        print 'invite ' + usr

    def on_msg(self, usr):
        print 'message ' + usr

    def on_enter(self, pos):
        self.lab['text_fg'] = self.menu_args.text_fg
        if self.invite_btn.is_hidden(): self.invite_btn.show()
        if self.msg_btn.is_hidden(): self.msg_btn.show()

    def on_exit(self, pos):
        self.lab['text_fg'] = self.menu_args.text_bg
        if not self.invite_btn.is_hidden(): self.invite_btn.hide()
        if not self.msg_btn.is_hidden(): self.msg_btn.hide()

    def destroy(self):
        self.lab.destroy()
        self.frm.destroy()


class MultiplayerFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.labels = []
        self.menu_args = menu_args
        self.frm = DirectFrame(
            frameSize=(-.02, .6, .05, -1.8), frameColor=(.2, .2, .2, .5),
            pos=(-.65, 1, 1.85), parent=base.a2dBottomRight)
        self.eng.xmpp.attach(self.on_users)
        self.set_connection_label()

    def set_connection_label(self):
        lab_args = self.menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        self.conn_lab = DirectLabel(
            text=_("You aren't logged in"), pos=(.3, 1, -.85), parent=self.frm,
            **lab_args)

    def on_users(self):
        map(lambda lab: lab.destroy(), self.labels)
        self.labels = []
        if not self.eng.xmpp.xmpp:
            self.set_connection_label()
        else:
            if self.conn_lab:
                self.conn_lab.destroy()
            for i, user in enumerate(self.eng.xmpp.users):
                lab = UserFrm(JID(user).bare, (0, 1, -.02 -.08 * i), self.frm, self.menu_args)
                self.labels += [lab]

    def destroy(self):
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
