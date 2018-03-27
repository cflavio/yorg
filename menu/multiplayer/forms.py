from direct.gui.DirectGuiGlobals import ENTER, EXIT
from yyagl.library.gui import Btn
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.observer import Subject
from .button import StaticMPBtn, MPBtn
from yyagl.gameobject import GameObject


class UserLabel(GameObject):

    def __init__(self, name, parent, menu_args, is_supporter, is_online, name_full):
        GameObject.__init__(self)
        self.menu_args = menu_args
        self.parent = parent
        self.name_full = name_full
        self.is_online = is_online
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        self.lab = DirectLabel(text=name, pos=(0, 1, 0), parent=parent,
                               text_align=TextNode.A_left, **lab_args)
        self.supp_btn = None
        self.set_supporter(is_supporter)
        self.set_online()

    def on_enter(self, pos): self.lab['text_fg'] = self.menu_args.text_active

    def on_exit(self, pos): self.lab['text_fg'] = self.menu_args.text_normal

    def set_supporter(self, is_supporter):
        if is_supporter:
            self.lab.set_x(.03)
            self.supp_btn = StaticMPBtn(
                self.parent, self, self.menu_args, 'assets/images/gui/medal.txo',
                .01, None, self.name_full, _('Supporter!'))
        else:
            self.lab.set_x(0)
            if self.supp_btn:
                self.supp_btn = self.supp_btn.destroy()

    def set_online(self, val=None):
        if val is not None: self.is_online = val
        if self.name_full == self.eng.xmpp.client.boundjid.full: self.is_online = True
        self.lab.set_alpha_scale(1 if self.is_online else .4)

    def destroy(self):
        self.lab.destroy()
        if self.supp_btn: self.supp_btn.destroy()
        GameObject.destroy(self)


class UserFrmMe(GameObject, Subject):

    def __init__(self, name, name_full, is_supporter, is_online, pos, parent,
                 menu_args, msg_btn_x=.58):
        Subject.__init__(self)
        GameObject.__init__(self)
        self.name_full = name_full
        self.menu_args = menu_args
        self.frm = Btn(
            frameSize=(-.01, .79, .05, -.03), frameColor=(1, 1, 1, 0),
            pos=pos, parent=parent)
        name = name.split('@')[0] + '\1smaller\1@' + name.split('@')[1] + '\2'
        self.lab = UserLabel(name, self.frm, menu_args, is_supporter, is_online, name_full)
        self.frm.bind(ENTER, self.on_enter)
        self.frm.bind(EXIT, self.on_exit)

    def on_enter(self, pos):
        self.lab.on_enter(pos)

    def on_exit(self, pos):
        self.lab.on_exit(pos)

    def destroy(self):
        self.lab.destroy()
        self.frm.destroy()
        Subject.destroy(self)
        GameObject.destroy(self)


class UserFrm(UserFrmMe):

    def __init__(self, name, name_full, is_supporter, is_online, pos, parent,
                 menu_args, msg_btn_x=.58):
        UserFrmMe.__init__(self, name, name_full, is_supporter, is_online, pos,
                           parent, menu_args, msg_btn_x)
        self.msg_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/message.txo',
            msg_btn_x, self.on_msg, name_full, _('send a message to the user'))

    def on_msg(self, usr):
        self.notify('on_add_chat', usr.name_full)

    def on_enter(self, pos):
        UserFrmMe.on_enter(self, pos)
        if self.msg_btn.is_hidden(): self.msg_btn.show()

    def on_exit(self, pos):
        UserFrmMe.on_exit(self, pos)
        if not self.msg_btn.is_hidden(): self.msg_btn.hide()


class UserFrmListMe(UserFrmMe):

    def __init__(self, name, name_full, is_supporter, pos, parent, menu_args):
        UserFrmMe.__init__(
            self, name, name_full, is_supporter, True, pos, parent, menu_args)

    def enable_invite_btn(self, enable=True): pass


class UserFrmList(UserFrm):

    def __init__(self, name, name_full, is_supporter, is_online, is_friend,
                 is_in_yorg, is_playing, pos, parent, menu_args):
        UserFrm.__init__(
            self, name, name_full, is_supporter, is_online, pos, parent,
            menu_args)
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_normal
        self.__enable_invite_btn = is_in_yorg and not is_playing
        self.invite_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/invite.txo',
            .65, self.on_invite, name_full.name, _("isn't playing yorg"))
        self.create_friend_btn(is_friend, menu_args, name_full)

    def create_friend_btn(self, is_friend, menu_args, name_full):
        if not is_friend:
            self.friend_btn = MPBtn(
                self.frm, self, menu_args, 'assets/images/gui/friend.txo',
                .72, self.on_friend, name_full.name, _('add to xmpp friends'))
        else:
            self.friend_btn = MPBtn(
                self.frm, self, menu_args, 'assets/images/gui/kick.txo',
                .72, self.on_unfriend, name_full.name,
                _('remove from xmpp friends'))

    def enable_invite_btn(self, enable=True): self.__enable_invite_btn = enable

    def on_invite(self, usr_name):
        self.eng.log('invite ' + usr_name)
        self.invite_btn.disable()
        self.notify('on_invite', self.eng.xmpp.find_usr(usr_name))

    def on_friend(self, usr_name):
        self.eng.log('friend with ' + usr_name)
        self.friend_btn.disable()
        self.notify('on_friend', usr_name)

    def on_enter(self, pos):
        UserFrm.on_enter(self, pos)
        if self.invite_btn.is_hidden():
            self.invite_btn.show()
            if not self.__enable_invite_btn: self.invite_btn.disable()
            else: self.invite_btn.enable()
        if self.friend_btn.is_hidden(): self.friend_btn.show()

    def on_exit(self, pos):
        UserFrm.on_exit(self, pos)
        if not self.invite_btn.is_hidden(): self.invite_btn.hide()
        if not self.friend_btn.is_hidden(): self.friend_btn.hide()

    def on_unfriend(self, usr):
        self.eng.log('unfriend with ' + usr)
        self.friend_btn.disable()
        self.notify('on_unfriend', usr)


class UserFrmMatch(UserFrm):

    def __init__(self, name, name_full, is_supporter, is_online, pos, parent,
                 menu_args):
        UserFrm.__init__(
            self, name, name_full, is_supporter, is_online, pos, parent,
            menu_args, 1.0)
        self.frm['frameSize'] = (-.01, 1.06, .05, -.03)
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        lab_args['text_fg'] = self.menu_args.text_normal
        self.remove_btn = MPBtn(
            self.frm, self, menu_args, 'assets/images/gui/remove.txo',
            .92, self.on_remove, name_full.name, _("remove from the match"))

    def on_remove(self, usr):
        self.notify('on_remove', usr)

    def on_enter(self, pos):
        UserFrm.on_enter(self, pos)
        if self.remove_btn.is_hidden():
            self.remove_btn.show()

    def on_exit(self, pos):
        UserFrm.on_exit(self, pos)
        if not self.remove_btn.is_hidden(): self.remove_btn.hide()
