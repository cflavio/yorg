from time import strftime
from sleekxmpp.jid import JID
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectLabel import DirectLabel
from yyagl.gameobject import GameObject
from yyagl.engine.logic import VersionChecker
from .forms import UserFrmListMe, UserFrmList, UserFrmListOut


class UsersFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.eng.log('create users form')
        self.ver_check = VersionChecker()
        self.room_name = None
        self.labels = []
        self.invited_users = []
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        self.users_lab = DirectLabel(
            text=_('Current online users'), pos=(-.85, 1, -.02),
            hpr=(0, 0, -90), parent=base.a2dTopRight,
            text_align=TextNode.A_right, **lab_args)
        self.frm = DirectScrolledFrame(
            frameSize=(-.02, .8, .45, 2.43),
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
            pos=(-.82, 1, -2.44), parent=base.a2dTopRight)
        self.set_connection_label()
        self.in_match_room = None

    def show(self):
        self.frm.show()
        self.users_lab.show()

    def hide(self):
        self.frm.hide()
        self.users_lab.hide()

    def set_connection_label(self):
        lab_args = self.menu_args.label_args
        lab_args['scale'] = .046
        if not self.ver_check.is_uptodate():
            txt = _("Your game isn't up-to-date, please update")
        else: txt = _("You aren't logged in")
        self.conn_lab = DirectLabel(
            text=txt, pos=(.38, 1, 1.0), parent=self.frm,
            text_wordwrap=10, **lab_args)

    def set_size(self, full=True):
        if full:
            self.frm.setPos(-.82, 1, -2.44)
            self.frm['frameSize'] = (-.02, .8, .45, 2.43)
        else:
            self.frm.setPos(-.82, 1, -1.97)
            self.frm['frameSize'] = (-.02, .8, .45, 1.96)

    @staticmethod
    def trunc(name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_users(self):
        if not self.eng.xmpp.client: self.set_connection_label()
        else:
            if self.conn_lab:
                self.conn_lab.destroy()
            bare_users = [self.trunc(user.name, 20)
                          for user in self.eng.xmpp.users]
            for lab in self.labels[:]:
                _lab = lab.lab['text'].replace('\1smaller\1', '').replace('\2', '')
                if _lab not in bare_users:
                    lab.destroy()
                    self.labels.remove(lab)
            nusers = len(self.eng.xmpp.users)
            invite_btn = len(self.invited_users) < 8
            invite_btn = invite_btn and not self.in_match_room
            top = .08 * nusers + .08
            self.frm['canvasSize'] = (-.02, .76, 0, top)
            label_users = [lab.lab['text'] for lab in self.labels]
            clean = lambda n: n.replace('\1smaller\1', '').replace('\2', '')
            label_users = map(clean, label_users)
            for i, user in enumerate(self.eng.xmpp.users):
                usr_inv = invite_btn and user.is_in_yorg
                if self.trunc(user.name, 20) not in label_users:
                    if self.eng.xmpp.client.boundjid.bare != user.name and \
                            user.is_in_yorg:
                        lab = UserFrmList(
                            self.trunc(user.name, 20),
                            user,
                            user.is_supporter,
                            self.eng.xmpp.is_friend(user.name),
                            (0, 1, top - .08 - .08 * i),
                            self.frm.getCanvas(),
                            self.menu_args)
                    elif self.eng.xmpp.client.boundjid.bare != user.name and \
                            not user.is_in_yorg:
                        lab = UserFrmListOut(
                            self.trunc(user.name, 20),
                            user,
                            user.is_supporter,
                            self.eng.xmpp.is_friend(user.name),
                            (0, 1, top - .08 - .08 * i),
                            self.frm.getCanvas(),
                            self.menu_args)
                        lab.enable_invite_btn(False)
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
                    lab.attach(self.on_add_chat)
                else:
                    clean = lambda n: n.replace('\1smaller\1', '').replace('\2', '')
                    lab = [lab for lab in self.labels
                           if clean(lab.lab['text']) == self.trunc(user.name, 20)][0]
                    lab.enable_invite_btn(
                        usr_inv and user.name not in self.invited_users)
                    lab.frm.set_z(top - .08 - .08 * i)
                    lab.set_supporter(user.is_supporter)

    def on_invite(self, usr):
        self.invited_users += [usr.name]
        self.notify('on_invite', usr)
        self.on_users()
        if not self.room_name:
            jid = self.eng.xmpp.client.boundjid
            time_code = strftime('%y%m%d%H%M%S')
            srv = self.eng.xmpp.client.conf_srv
            self.room_name = 'yorg' + jid.user + time_code + '@' + srv
            self.eng.xmpp.client.plugin['xep_0045'].joinMUC(
                self.room_name, self.eng.xmpp.client.boundjid.bare,
                pfrom=self.eng.xmpp.client.boundjid.full)
            cfg = self.eng.xmpp.client.plugin['xep_0045'].getRoomConfig(self.room_name)
            values = cfg.get_values()
            values['muc#roomconfig_publicroom'] = False
            cfg.set_values(values)
            self.eng.xmpp.client.plugin['xep_0045'].configureRoom(self.room_name, cfg)
            self.eng.log('created room ' + self.room_name)
        self.eng.xmpp.client.send_message(
            mfrom=self.eng.xmpp.client.boundjid.full,
            mto=usr.name_full,
            mtype='chat',
            msubject='invite',
            mbody=self.room_name)
        self.eng.log('invited ' + str(usr.name_full))
        self.notify('on_add_groupchat', self.room_name, usr.name)

    def on_declined(self, msg):
        self.eng.log('declined from ' + str(JID(msg['from']).bare))
        usr = str(JID(msg['from']).bare)
        self.invited_users.remove(usr)
        self.on_users()

    def on_add_chat(self, msg): self.notify('on_add_chat', msg)

    def on_friend(self, usr):
        self.eng.log('send friend to ' + usr.name)
        self.eng.xmpp.client.send_presence_subscription(
            usr.name, ptype='subscribe',
            pfrom=self.eng.xmpp.client.boundjid.full)

    def on_unfriend(self, usr):
        self.eng.log('roster ' + str(self.eng.xmpp.client.client_roster))
        self.eng.xmpp.client.del_roster_item(usr.name)
        self.eng.log('roster ' + str(self.eng.xmpp.client.client_roster))

    def destroy(self):
        self.eng.log('destroyed usersfrm')
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
