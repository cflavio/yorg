from direct.gui.DirectDialog import YesNoDialog
from direct.gui.DirectGuiGlobals import ENTER, EXIT, FLAT
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.observer import Subject
from yyagl.engine.logic import VersionChecker


class FriendDialog(Subject):

    def __init__(self, menu_args, user):
        Subject.__init__(self)
        self.user = user
        self.dialog = YesNoDialog(
            base.a2dBottomLeft,
            text=_('Can %s add you to her XMPP contacts?') % user,
            text_wordwrap=16,
            text_fg=menu_args.text_fg,
            text_font=menu_args.font,
            pad=(.03, .03),
            topPad=0,
            midPad=.01,
            relief=FLAT,
            frameColor=(.8, .8, .8, .9),
            button_relief=FLAT,
            button_frameColor=(.2, .2, .2, .2),
            button_text_fg=menu_args.text_fg,
            button_text_font=menu_args.font,
            buttonValueList=['yes', 'no'],
            command=self.on_btn)
        size = self.dialog['frameSize']
        self.dialog.set_pos(-size[0] + .05, 1, -size[2] + .05)

    def on_btn(self, val):
        self.notify('on_friend_answer', self.user, val == 'yes')

    def destroy(self):
        self.dialog = self.dialog.destroy()
        Subject.destroy(self)


class MPBtn(object):

    tooltip_align = TextNode.A_right
    tooltip_offset = (.01, 0, -.08)

    def __init__(self, parent, owner, menu_args, img_path, msg_btn_x, cb, usr,
                 tooltip):
        self.owner = owner
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = menu_args.text_bg
        self.btn = ImgBtn(
            parent=parent, scale=.024, pos=(msg_btn_x, 1, .01),
            frameColor=(1, 1, 1, 1), frameTexture=img_path, command=cb,
            extraArgs=[usr], **menu_args.imgbtn_args)
        self.btn.bind(ENTER, self.on_enter)
        self.btn.bind(EXIT, self.on_exit)
        self.on_create()
        self.tooltip = DirectLabel(
            text=tooltip, pos=self.btn.get_pos() + self.tooltip_offset,
            parent=parent, text_wordwrap=10, text_bg=(.2, .2, .2, .8),
            text_align=self.tooltip_align, **lab_args)
        self.tooltip.set_bin('gui-popup', 10)
        self.tooltip.hide()

    def on_create(self): self.btn.hide()

    def is_hidden(self): return self.btn.is_hidden()

    def show(self): return self.btn.show()

    def hide(self): return self.btn.hide()

    def enable(self): return self.btn.enable()

    def disable(self): return self.btn.disable()

    def on_enter(self, pos):
        self.owner.on_enter(pos)
        self.tooltip.show()

    def on_exit(self, pos):
        self.owner.on_exit(pos)
        self.tooltip.hide()


class StaticMPBtn(MPBtn):

    tooltip_align = TextNode.A_left
    tooltip_offset = (.01, 0, .05)

    def on_create(self): pass


class UserFrmMe(Subject):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args,
                 msg_btn_x=.58):
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
            self.supp_btn = StaticMPBtn(
                self.frm, self, menu_args, 'assets/images/gui/medal.txo',
                .01, None, name_full, _('Supporter!'))

    def on_enter(self, pos): self.lab['text_fg'] = self.menu_args.text_fg

    def on_exit(self, pos): self.lab['text_fg'] = self.menu_args.text_bg

    def destroy(self):
        self.lab.destroy()
        self.frm.destroy()
        Subject.destroy(self)


class UserFrm(UserFrmMe):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args,
                 msg_btn_x=.58):
        UserFrmMe.__init__(self, name, name_full, is_supporter, pos, parent,
                           menu_args, msg_btn_x)
        self.msg_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/message.txo',
            msg_btn_x, self.on_msg, name_full, _('send a message to the user'))

    def on_msg(self, usr): print 'message ' + usr.name

    def on_enter(self, pos):
        UserFrmMe.on_enter(self, pos)
        if self.msg_btn.is_hidden(): self.msg_btn.show()

    def on_exit(self, pos):
        UserFrmMe.on_exit(self, pos)
        if not self.msg_btn.is_hidden(): self.msg_btn.hide()


class UserFrmListMe(UserFrmMe):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args):
        UserFrmMe.__init__(
            self, name, name_full, is_supporter, pos, parent, menu_args)

    def show_invite_btn(self, show=True): pass


class UserFrmListOut(UserFrm):

    def __init__(self, name, name_full, is_supporter, is_friend, pos, parent,
                 menu_args):
        UserFrm.__init__(
            self, name, name_full, is_supporter, pos, parent, menu_args)
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_bg
        self.__show_invite_btn = True
        self.invite_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/invite.txo',
            .65, self.on_invite, name_full, _("isn't playing yorg"))
        self.create_friend_btn(is_friend, menu_args, name_full)

    def create_friend_btn(self, is_friend, menu_args, name_full):
        self.friend_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/kick.txo',
            .72, self.on_unfriend, name_full, _('remove from xmpp friends'))

    def show_invite_btn(self, show=True): self.__show_invite_btn = show

    def on_invite(self, usr): pass

    def on_enter(self, pos):
        UserFrm.on_enter(self, pos)
        if self.invite_btn.is_hidden():
            self.invite_btn.show()
            if not self.__show_invite_btn: self.invite_btn.disable()
        if self.friend_btn.is_hidden(): self.friend_btn.show()

    def on_exit(self, pos):
        UserFrm.on_exit(self, pos)
        if not self.invite_btn.is_hidden(): self.invite_btn.hide()
        if not self.friend_btn.is_hidden(): self.friend_btn.hide()

    def on_unfriend(self, usr):
        self.friend_btn.disable()
        self.notify('on_unfriend', usr)


class UserFrmList(UserFrmListOut):

    def create_friend_btn(self, is_friend, menu_args, name_full):
        if not is_friend:
            self.friend_btn = MPBtn(
                self.frm, self, menu_args, 'assets/images/gui/friend.txo',
                .72, self.on_friend, name_full, _('add to xmpp friends'))
        else:
            self.friend_btn = MPBtn(
                self.frm, self, menu_args, 'assets/images/gui/kick.txo',
                .72, self.on_unfriend, name_full,
                _('remove from xmpp friends'))

    def on_invite(self, usr):
        print 'invite ' + usr.name
        self.invite_btn.disable()
        self.notify('on_invite', usr)

    def on_friend(self, usr):
        self.friend_btn.disable()
        self.notify('on_friend', usr)


class MultiplayerFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.dialog = None
        self.ver_check = VersionChecker()
        self.labels = []
        self.invited_users = []
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = menu_args.text_bg
        self.users_lab = DirectLabel(
            text=_('Current online users'), pos=(-.85, 1, -.02),
            hpr=(0, 0, -90), parent=base.a2dTopRight,
            text_align=TextNode.A_right, **lab_args)
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
            parent=base.a2dBottomRight, text_align=TextNode.A_right,
            **lab_args)
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
        self.eng.xmpp.attach(self.on_user_subscribe)
        self.eng.xmpp.attach(self.on_presence_available)
        self.eng.xmpp.attach(self.on_presence_unavailable)
        self.set_connection_label()

    def show(self):
        self.frm.show()
        self.users_lab.show()
        self.match_lab.show()
        self.match_frm.show()
        self.msg_frm.show()

    def hide(self):
        self.frm.hide()
        self.users_lab.hide()
        self.match_lab.hide()
        self.match_frm.hide()
        self.msg_frm.hide()

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

    @staticmethod
    def trunc(name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_user_subscribe(self, user):
        self.dialog = FriendDialog(self.menu_args, user)
        self.dialog.attach(self.on_friend_answer)

    def on_friend_answer(self, user, val):
        self.dialog.detach(self.on_friend_answer)
        self.dialog = self.dialog.destroy()
        self.eng.xmpp.xmpp.send_presence_subscription(
            pto=user,
            pfrom=self.eng.xmpp.xmpp.boundjid.full,
            ptype='subscribed' if val else 'unsubscribed')

    def on_user_connected(self, user): self.on_users()

    def on_user_disconnected(self, user): self.on_users()

    def on_presence_available(self, user): self.on_users()

    def on_presence_unavailable(self, user): self.on_users()

    def on_users(self):
        if not self.eng.xmpp.xmpp: self.set_connection_label()
        else:
            if self.conn_lab:
                self.conn_lab.destroy()
            bare_users = [self.trunc(user.name, 20)
                          for user in self.eng.xmpp.users]
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
                usr_inv = invite_btn and user.is_in_yorg
                if self.trunc(user.name, 20) not in label_users:
                    if self.eng.xmpp.xmpp.boundjid.bare != user.name and \
                            user.is_in_yorg:
                        lab = UserFrmList(
                            self.trunc(user.name, 20),
                            user,
                            user.is_supporter,
                            self.eng.xmpp.is_friend(user.name),
                            (0, 1, top - .08 - .08 * i),
                            self.frm.getCanvas(),
                            self.menu_args)
                    elif self.eng.xmpp.xmpp.boundjid.bare != user.name and \
                            not user.is_in_yorg:
                        lab = UserFrmListOut(
                            self.trunc(user.name, 20),
                            user,
                            user.is_supporter,
                            self.eng.xmpp.is_friend(user.name),
                            (0, 1, top - .08 - .08 * i),
                            self.frm.getCanvas(),
                            self.menu_args)
                        lab.show_invite_btn(False)
                    else:
                        lab = UserFrmListMe(
                            self.trunc(user.name, 20),
                            user,
                            user.is_supporter,
                            (0, 1, top - .08 - .08 * i),
                            self.frm.getCanvas(),
                            self.menu_args)
                    self.labels += [lab]
                    lab.attach(self.on_invite)
                    lab.attach(self.on_friend)
                    lab.attach(self.on_unfriend)
                else:
                    lab = [lab for lab in self.labels
                           if lab.lab['text'] == self.trunc(user.name, 20)][0]
                    lab.show_invite_btn(
                        usr_inv and user.name not in self.invited_users)
                    lab.frm.set_z(top - .08 - .08 * i)

    def on_invite(self, usr):
        print 'invited user', usr
        idx = len(self.invited_users)
        x = .02 + .4 * (idx / 4)
        y = .38 - .08 * (idx % 4)
        UserFrm(self.trunc(usr.name, 8), usr, usr.is_supporter, (x, 1, y),
                self.match_frm, self.menu_args, .32)
        self.invited_users += [usr.name]
        self.on_users()

    def on_friend(self, usr):
        self.eng.xmpp.xmpp.send_presence_subscription(
            usr.name, ptype='subscribe',
            pfrom=self.eng.xmpp.xmpp.boundjid.full)

    def on_unfriend(self, usr):
        print '\n\n', self.eng.xmpp.xmpp.client_roster, '\n\n'
        self.eng.xmpp.xmpp.del_roster_item(usr.name)
        print '\n\n', self.eng.xmpp.xmpp.client_roster, '\n\n'

    def on_start(self): print 'start'

    def destroy(self):
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
