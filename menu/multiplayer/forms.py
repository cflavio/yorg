from direct.gui.DirectGuiGlobals import ENTER, EXIT
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.observer import Subject
from .button import StaticMPBtn, MPBtn


class UserFrmMe(Subject):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args,
                 msg_btn_x=.58):
        Subject.__init__(self)
        self.name_full = name_full
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
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

    def on_enter(self, pos): self.lab['text_fg'] = self.menu_args.text_active

    def on_exit(self, pos): self.lab['text_fg'] = self.menu_args.text_normal

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

    def on_msg(self, usr): self.notify('on_add_chat', usr.name)

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
        lab_args['text_fg'] = self.menu_args.text_normal
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
