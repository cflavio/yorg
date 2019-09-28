from logging import info
from time import strftime
from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import FLAT
from json import load
from urllib.request import urlopen
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from yyagl.gameobject import GameObject
from yyagl.engine.logic import VersionChecker
from yyagl.lib.gui import Label
from .forms import UserFrmListMe, UserFrmList


class UsersFrm(GameObject):

    def __init__(self, menu_props, yorg_srv):
        GameObject.__init__(self)
        info('create users form')
        self.ver_check = VersionChecker()
        self.yorg_srv = yorg_srv
        self.room_name = None
        self.labels = []
        self.invited_users = []
        self.menu_props = menu_props
        lab_args = menu_props.label_args
        lab_args['scale'] = .046
        self.users_lab = Label(
            text=_('Current online users'), pos=(-.85, -.02),
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
        self.conn_lab = Label(
            text='', pos=(.38, 1.5), parent=self.frm,
            text_wordwrap=10, **lab_args)
        self.set_connection_label()
        self.in_match_room = None
        self.invited = False

    def show(self):
        self.frm.show()
        self.users_lab.show()

    def hide(self):
        self.frm.hide()
        self.users_lab.hide()

    def set_connection_label(self):
        lab_args = self.menu_props.label_args
        lab_args['scale'] = .046
        txt = ''
        if not self.ver_check.is_uptodate():
            txt = _("Your game isn't up-to-date, please update")
        elif not self.eng.client.is_server_up:
            txt = _("Yorg's server isn't running")
        elif not self.eng.client.authenticated: txt = _("You aren't logged in")
        (self.conn_lab.show if txt else self.conn_lab.hide)()
        self.conn_lab['text'] = txt

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
        self.set_connection_label()
        bare_users = [self.trunc(user.uid, 20)
                      for user in self.eng.client.sorted_users]
        for lab in self.labels[:]:
            _lab = lab.lab.lab['text'].replace('\1smaller\1', '').replace('\2', '')
            if _lab not in bare_users:
                if _lab not in self.eng.client.users:
                    lab.destroy()
                    self.labels.remove(lab)
        nusers = len(self.eng.client.sorted_users)
        invite_btn = len(self.invited_users) < 8
        invite_btn = invite_btn and not self.in_match_room and not self.invited
        top = .08 * nusers + .08
        self.frm['canvasSize'] = (-.02, .76, 0, top)
        label_users = [lab.lab.lab['text'] for lab in self.labels]
        clean = lambda n: n.replace('\1smaller\1', '').replace('\2', '')
        label_users = list(map(clean, label_users))
        for i, user in enumerate(self.eng.client.sorted_users):
            if self.trunc(user.uid, 20) not in label_users:
                if self.eng.client.myid != user.uid:
                    lab = UserFrmList(
                        user.uid,
                        user.is_supporter,
                        user.is_playing,
                        (0, 1, top - .08 - .08 * i),
                        self.frm.getCanvas(),
                        self.menu_props)
                else:
                    lab = UserFrmListMe(
                        user.uid,
                        user.is_supporter,
                        (0, 1, top - .08 - .08 * i),
                        self.frm.getCanvas(),
                        self.menu_props)
                self.labels += [lab]
                lab.attach(self.on_invite)
                lab.attach(self.on_friend)
                lab.attach(self.on_unfriend)
                lab.attach(self.on_add_chat)
        #for i, user in enumerate(self.eng.client.sorted_users):
        #    clean = lambda n: n.replace('\1smaller\1', '').replace('\2', '')
        #    lab = [lab for lab in self.labels
        #           if clean(lab.lab.lab['text']) == self.trunc(user.uid, 20)][0]
        #    enb_val = invite_btn and user.uid not in self.invited_users and not user.is_playing
        #    if hasattr(lab, 'invite_btn'):
        #        inv_btn = lab.invite_btn
        #        if enb_val: inv_btn.tooltip['text'] = _('invite the user to a match')
        #        elif len(self.invited_users) == 8: inv_btn.tooltip['text'] = _("you can't invite more players")
        #        elif self.in_match_room: inv_btn.tooltip['text'] = _("you're already in a match")
        #        elif user.uid in self.invited_users: inv_btn.tooltip['text'] = _("you've already invited this user")
        #        elif user.is_playing: inv_btn.tooltip['text'] = _("the user is already playing a match")
        #    lab.enable_invite_btn(enb_val)
        #    lab.frm.set_z(top - .08 - .08 * i)
        #    lab.lab.set_supporter(user.is_supporter)

    def on_invite(self, usr):
        self.notify('on_invite', usr)
        self.invited_users += [usr.uid]
        self.on_users()
        if not self.room_name:

            time_code = strftime('%y%m%d%H%M%S')
            self.room_name = self.eng.client.myid + time_code
            #self.eng.xmpp.client.plugin['xep_0045'].joinMUC(
            #    self.room_name, self.eng.xmpp.client.boundjid.bare,
            #    pfrom=self.eng.xmpp.client.boundjid.full)
            #cfg = self.eng.xmpp.client.plugin['xep_0045'].getRoomConfig(self.room_name)
            #values = cfg.get_values()
            #values['muc#roomconfig_publicroom'] = False
            #cfg.set_values(values)
            #self.eng.xmpp.client.plugin['xep_0045'].configureRoom(self.room_name, cfg)
            self.eng.client.register_rpc('join_room')
            self.eng.client.join_room(self.room_name)
            info('created room ' + self.room_name)
            self.eng.client.is_server_active = True
            #for usr_name in [self.yorg_srv] + \
            #    [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            #    self.eng.xmpp.client.send_message(
            #        mfrom=self.eng.xmpp.client.boundjid.full,
            #        mto=usr_name,
            #        mtype='ya2_yorg',
            #        msubject='is_playing',
            #        mbody='1')
        self.eng.client.register_rpc('invite')
        ret = self.eng.client.invite(usr.uid, self.room_name)
        #self.eng.xmpp.client.send_message(
        #    mfrom=self.eng.xmpp.client.boundjid.full,
        #    mto=usr.name_full,
        #    mtype='ya2_yorg',
        #    msubject='invite',
        #    mbody=self.room_name + '\n' + self.eng.server.public_addr + '\n' + self.eng.server.local_addr)
        if ret == 'ok':
            info('invited ' + str(usr.uid))
            self.notify('on_add_groupchat', self.room_name, usr.uid)

    def on_declined(self, from_):
        info('declined from ' + from_)
        self.invited_users.remove(from_)
        self.on_users()

    def on_add_chat(self, msg): self.notify('on_add_chat', msg)

    def on_logout(self):
        list(map(lambda lab: lab.destroy(), self.labels))
        self.labels = []

    def on_friend(self, usr_name):
        info('send friend to ' + usr_name)
        self.eng.xmpp.client.send_presence_subscription(
            usr_name, ptype='subscribe',
            pfrom=self.eng.xmpp.client.boundjid.full)

    def on_unfriend(self, usr):
        info('roster ' + str(self.eng.xmpp.client.client_roster))
        self.eng.xmpp.client.del_roster_item(usr)
        info('roster ' + str(self.eng.xmpp.client.client_roster))

    def destroy(self):
        info('destroyed usersfrm')
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
