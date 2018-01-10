from direct.gui.DirectGuiGlobals import ENTER, EXIT, FLAT
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.engine.gui.page import PageGui
from yyagl.observer import Subject
from yyagl.engine.logic import VersionChecker


try:
    from sleekxmpp.jid import JID
except ImportError:  # sleekxmpp requires openssl 1.0.2
    print 'OpenSSL 1.0.2 not detected'


class UserFrm(Subject):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args, msg_btn_x=.58):
        Subject.__init__(self)
        self.name_full = name_full
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        self.frm = DirectButton(
            frameSize=(-.01, .79, .05, -.03), frameColor=(1, 1, 1, 0),
            pos=pos, parent=parent)
        self.frm.bind(ENTER, self.on_enter)
        self.frm.bind(EXIT, self.on_exit)
        self.lab = DirectLabel(text=name, pos=(0, 1, 0), parent=self.frm,
                               text_align=TextNode.A_left, **lab_args)
        self.lab.bind(ENTER, self.on_enter)
        self.lab.bind(EXIT, self.on_exit)
        if is_supporter:
            self.lab.set_x(.03)
            self.supp_btn = ImgBtn(
                    parent=self.frm,
                    scale=.024,
                    pos=(.01, 1, .01),
                    frameColor=(1, 1, 1, 1),
                    frameTexture='assets/images/gui/medal.txo',
                    **menu_args.imgbtn_args)
            self.supp_btn.bind(ENTER, self.on_enter_supp)
            self.supp_btn.bind(EXIT, self.on_exit_supp)
            self.supp_tooltip = DirectLabel(
                text=_('Supporter!'),
                pos=self.supp_btn.get_pos() + (.01, 0, .05), parent=self.frm,
                text_wordwrap=10, text_bg=(.2, .2, .2, .8),
                text_align=TextNode.A_left, **lab_args)
            self.supp_tooltip.set_bin('gui-popup', 10)
            self.supp_tooltip.hide()
        self.msg_btn = ImgBtn(
                parent=self.frm,
                scale=.024,
                pos=(msg_btn_x, 1, .01),
                frameColor=(1, 1, 1, 1),
                frameTexture='assets/images/gui/message.txo',
                command=self.on_msg,
                extraArgs=[name],
                **menu_args.imgbtn_args)
        self.msg_btn.bind(ENTER, self.on_enter_msg)
        self.msg_btn.bind(EXIT, self.on_exit_msg)
        self.msg_btn.hide()
        self.msg_tooltip = DirectLabel(
            text=_('send a message to the user'),
            pos=self.msg_btn.get_pos() + (.01, 0, -.08), parent=self.frm,
            text_wordwrap=10, text_bg=(.2, .2, .2, .8),
            text_align=TextNode.A_right, **lab_args)
        self.msg_tooltip.set_bin('gui-popup', 10)
        self.msg_tooltip.hide()

    def on_msg(self, usr):
        print 'message ' + usr

    def on_enter(self, pos):
        self.lab['text_fg'] = self.menu_args.text_fg
        if self.msg_btn.is_hidden(): self.msg_btn.show()

    def on_exit(self, pos):
        self.lab['text_fg'] = self.menu_args.text_bg
        if not self.msg_btn.is_hidden(): self.msg_btn.hide()

    def on_enter_msg(self, pos):
        self.on_enter(pos)
        self.msg_tooltip.show()

    def on_exit_msg(self, pos):
        self.on_exit(pos)
        self.msg_tooltip.hide()

    def on_enter_supp(self, pos):
        self.on_enter(pos)
        self.supp_tooltip.show()

    def on_exit_supp(self, pos):
        self.on_exit(pos)
        self.supp_tooltip.hide()

    def destroy(self):
        self.lab.destroy()
        self.frm.destroy()
        Subject.destroy(self)


class UserFrmList(UserFrm):

    def __init__(self, name, name_full, is_supporter, is_friend, pos, parent, menu_args):
        UserFrm.__init__(self, name, name_full, is_supporter, pos, parent, menu_args)
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        self.__show_invite_btn = True
        self.invite_btn = ImgBtn(
                parent=self.frm,
                scale=.024,
                pos=(.65, 1, .01),
                frameColor=(1, 1, 1, 1),
                frameTexture='assets/images/gui/invite.txo',
                command=self.on_invite,
                extraArgs=[self.name_full],
                **menu_args.imgbtn_args)
        self.invite_btn.bind(ENTER, self.on_enter_invite)
        self.invite_btn.bind(EXIT, self.on_exit_invite)
        self.invite_btn.hide()
        self.invite_tooltip = DirectLabel(
            text=_('invite the user for a match'),
            pos=self.invite_btn.get_pos() + (.01, 0, -.08), parent=self.frm,
            text_bg=(.2, .2, .2, .8), text_align=TextNode.A_right,
            text_wordwrap=10, **lab_args)
        self.invite_tooltip.set_bin('gui-popup', 10)
        self.invite_tooltip.hide()
        self.friend_btn = ImgBtn(
                parent=self.frm,
                scale=.024,
                pos=(.72, 1, .01),
                frameColor=(1, 1, 1, 1),
                frameTexture='assets/images/gui/friend.txo',
                command=self.on_friend,
                extraArgs=[self.name_full],
                **menu_args.imgbtn_args)
        self.friend_btn.bind(ENTER, self.on_enter_friend)
        self.friend_btn.bind(EXIT, self.on_exit_friend)
        self.friend_btn.hide()
        self.friend_tooltip = DirectLabel(
            text=_('add to xmpp friends'),
            pos=self.friend_btn.get_pos() + (.01, 0, -.08), parent=self.frm,
            text_bg=(.2, .2, .2, .8), text_align=TextNode.A_right,
            text_wordwrap=10, **lab_args)
        self.friend_tooltip.set_bin('gui-popup', 10)
        self.friend_tooltip.hide()

    def show_invite_btn(self, show=True):
        self.__show_invite_btn = show

    def on_enter(self, pos):
        UserFrm.on_enter(self, pos)
        if self.invite_btn.is_hidden():
            self.invite_btn.show()
            if not self.__show_invite_btn: self.invite_btn.disable()
        if self.friend_btn.is_hidden():
            self.friend_btn.show()

    def on_exit(self, pos):
        UserFrm.on_exit(self, pos)
        if not self.invite_btn.is_hidden(): self.invite_btn.hide()
        if not self.friend_btn.is_hidden(): self.friend_btn.hide()

    def on_invite(self, usr):
        print 'invite ' + usr.name
        self.invite_btn.disable()
        self.notify('on_invite', usr)

    def on_enter_invite(self, pos):
        self.on_enter(pos)
        self.invite_tooltip.show()

    def on_exit_invite(self, pos):
        self.on_exit(pos)
        self.invite_tooltip.hide()

    def on_friend(self, usr):
        print 'friend ' + usr.name
        self.friend_btn.disable()
        self.notify('on_friend', usr)

    def on_enter_friend(self, pos):
        self.on_enter(pos)
        self.friend_tooltip.show()

    def on_exit_friend(self, pos):
        self.on_exit(pos)
        self.friend_tooltip.hide()


class MultiplayerFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.ver_check = VersionChecker()
        self.labels = []
        self.invited_users = []
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = menu_args.text_bg
        self.users_lab = DirectLabel(
            text=_('Current online users'), pos=(-.85, 1, -.02), hpr=(0, 0, -90),
            parent=base.a2dTopRight, text_align=TextNode.A_right, **lab_args)
        self.frm = DirectScrolledFrame(
            frameSize=(-.02, .8, .45, 1.48),
            canvasSize=(-.02, .76, -.08, 3.8),
            scrollBarWidth=.036,
            verticalScroll_relief=FLAT,
            verticalScroll_frameColor=(.2, .2, .2, .4),
            verticalScroll_thumb_relief=FLAT,
            verticalScroll_thumb_frameColor=(.8, .8, .8, .6),
            verticalScroll_incButton_relief=FLAT,
            verticalScroll_incButton_frameColor=(.8, .8, .8, .6),
            verticalScroll_decButton_relief=FLAT,
            verticalScroll_decButton_frameColor=(.8, .8, .8, .6),
            horizontalScroll_relief=FLAT,
            frameColor=(.2, .2, .2, .5),
            pos=(-.82, 1, -1.49), parent=base.a2dTopRight)
        self.match_lab = DirectLabel(
            text=_('Current match'), pos=(-.85, 1, .93), hpr=(0, 0, -90),
            parent=base.a2dBottomRight, text_align=TextNode.A_right, **lab_args)
        self.match_frm = DirectFrame(
            frameSize=(-.02, .8, 0, .45),
            frameColor=(.2, .2, .2, .5),
            pos=(-.82, 1, .49), parent=base.a2dBottomRight)
        self.msg_frm = DirectFrame(
            frameSize=(-.02, .8, 0, .45),
            frameColor=(.2, .2, .2, .5),
            pos=(-.82, 1, .02), parent=base.a2dBottomRight)
        btn_args = self.menu_args.btn_args
        btn_args['scale'] = .06
        DirectButton(text=_('Start'), pos=(.39, 1, .03), command=self.on_start,
                     parent=self.match_frm, **btn_args)
        self.eng.xmpp.attach(self.on_users)
        self.eng.xmpp.attach(self.on_user_connected)
        self.eng.xmpp.attach(self.on_user_disconnected)
        self.set_connection_label()

    def set_connection_label(self):
        lab_args = self.menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        if not self.ver_check.is_uptodate():
            txt = _("Your game isn't up-to-date, please update")
        else: txt = _("You aren't logged in")
        self.conn_lab = DirectLabel(
            text=txt, pos=(.38, 1, 1.0), parent=self.frm,
            text_wordwrap=10, **lab_args)

    def trunc(self, name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_user_connected(self, user):
        self.on_users()

    def on_user_disconnected(self, user):
        self.on_users()

    def on_users(self):
        if not self.eng.xmpp.xmpp:
            self.set_connection_label()
        else:
            if self.conn_lab:
                self.conn_lab.destroy()
            bare_users = [self.trunc(user.name, 20) for user in self.eng.xmpp.users]
            for lab in self.labels[:]:
                if lab.lab['text'] not in bare_users:
                    lab.destroy()
                    self.labels.remove(lab)
            nusers = len(self.eng.xmpp.users)
            invite_btn = len(self.invited_users) < 8
            top = .08 * nusers + .08
            self.frm['canvasSize'] = (-.02, .76, 0, top)
            label_users = [lab.lab['text'] for lab in self.labels]
            for i, user in enumerate(self.eng.xmpp.users):
                if self.trunc(user.name, 20) not in label_users:
                    lab = UserFrmList(
                        self.trunc(user.name, 20),
                        user,
                        user.is_supporter,
                        self.eng.xmpp.is_friend(user.name),
                        (0, 1, top - .08 -.08 * i),
                        self.frm.getCanvas(),
                        self.menu_args)
                    self.labels += [lab]
                    lab.attach(self.on_invite)
                    lab.attach(self.on_friend)
                else:
                    lab = [lab for lab in self.labels if lab.lab['text'] == self.trunc(user.name, 20)][0]
                    lab.show_invite_btn(invite_btn and user.name not in self.invited_users)
                    lab.frm.set_z(top - .08 -.08 * i)

    def on_invite(self, usr):
        print 'invited user', usr
        idx = len(self.invited_users)
        x = .02 + .4 * (idx / 4)
        y = .38 -.08 * (idx % 4)
        UserFrm(self.trunc(usr.name, 8), usr.name_full, usr.is_supporter, (x, 1, y), self.match_frm, self.menu_args, .32)
        self.invited_users += [usr.name]
        self.on_users()  # refactor: it's slow - don't recreate but edit
                         # current entries

    def on_friend(self, usr):
        self.eng.xmpp.xmpp.send_presence_subscription(
            usr.name,
            pfrom=self.eng.xmpp.xmpp.boundjid.full)

    def on_start(self):
        print 'start'

    def destroy(self):
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
