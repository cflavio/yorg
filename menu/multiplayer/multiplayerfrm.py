from json import load
from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from urllib2 import urlopen
try: from sleekxmpp.jid import JID
except ImportError:  # sleekxmpp requires openssl 1.0.2
    print 'OpenSSL 1.0.2 not detected'
from yyagl.gameobject import GameObject
from yyagl.engine.logic import VersionChecker
from menu.netmsgs import NetMsgs
from .usersfrm import UsersFrm
from .matchfrm import MatchFrmServer, MatchFrmServerClient
from .messagefrm import MessageFrm
from .friend_dlg import FriendDialog
from .invite_dlg import InviteDialog
from .exit_dlg import ExitDialog
from .remove_dlg import RemovedDialog


class MultiplayerFrm(GameObject):

    def __init__(self, menu_args, yorg_srv):
        GameObject.__init__(self)
        self.eng.log('created multiplayer form')
        self.dialog = None
        self.invite_dlg = None
        self.yorg_srv = yorg_srv
        self.ver_check = VersionChecker()
        self.labels = []
        self.invited_users = []
        self.menu_args = menu_args
        self.users_frm = UsersFrm(menu_args, yorg_srv)
        self.users_frm.attach(self.on_invite)
        self.users_frm.attach(self.on_add_chat)
        self.users_frm.attach(self.on_add_groupchat)
        self.msg_frm = MessageFrm(menu_args)
        self.msg_frm.attach(self.on_msg_focus)
        self.msg_frm.attach(self.on_close_all_chats)
        self.match_frm = None
        #self.match_frm.hide()
        self.msg_frm.hide()
        self.eng.xmpp.attach(self.on_users)
        self.eng.xmpp.attach(self.on_user_connected)
        self.eng.xmpp.attach(self.on_user_disconnected)
        self.eng.xmpp.attach(self.on_user_subscribe)
        self.eng.xmpp.attach(self.on_presence_available)
        self.eng.xmpp.attach(self.on_presence_available_room)
        self.eng.xmpp.attach(self.on_presence_unavailable_room)
        self.eng.xmpp.attach(self.on_presence_unavailable)
        self.eng.xmpp.attach(self.on_msg)
        self.eng.xmpp.attach(self.on_groupchat_msg)
        self.eng.xmpp.attach(self.on_invite_chat)
        self.eng.xmpp.attach(self.on_declined)
        self.eng.xmpp.attach(self.on_cancel_invite)
        self.eng.xmpp.attach(self.on_ip_address)
        self.eng.xmpp.attach(self.on_yorg_init)
        self.eng.xmpp.attach(self.on_is_playing)

    def create_match_frm(self, room, is_server):
        cls = MatchFrmServer if is_server else MatchFrmServerClient
        self.match_frm = cls(self.menu_args)
        self.match_frm.attach(self.on_start)
        self.match_frm.show(room)

    def show(self):
        self.eng.log('multiplayer form: show')
        self.users_frm.show()
        #self.match_frm.show()
        self.msg_frm.show()

    def hide(self):
        self.eng.log('multiplayer form: hide')
        self.users_frm.hide()
        #self.match_frm.hide()
        self.msg_frm.hide()

    def on_user_subscribe(self, user):
        self.eng.log('user subscribe: ' + str(user))
        if self.eng.xmpp.is_friend(user): return
        self.dialog = FriendDialog(self.menu_args, user)
        self.dialog.attach(self.on_friend_answer)

    def on_friend_answer(self, user, val):
        self.dialog.detach(self.on_friend_answer)
        self.dialog = self.dialog.destroy()
        self.eng.log('send presence subscription to %s: %s' %(user, 'subscribed' if val else 'unsubscribed'))
        self.eng.xmpp.client.send_presence_subscription(
            pto=user,
            pfrom=self.eng.xmpp.client.boundjid.full,
            ptype='subscribed' if val else 'unsubscribed')
        self.on_users()

    def on_invite(self, usr):
        if not self.match_frm:
            self.create_match_frm('', True)
            self.eng.server.start(self.process_msg_srv, self.process_connection)
        self.match_frm.on_invite(usr)

    def process_msg_srv(data_lst):
        print data_lst

    def process_connection(self, client_address):
        self.eng.log_mgr.log('connection from ' + client_address)

    def on_users(self): self.users_frm.on_users()

    def on_user_connected(self, user):
        self.eng.log('user connected ' + user)
        self.users_frm.on_users()

    def on_user_disconnected(self, user):
        self.eng.log('user disconnected ' + user)
        self.users_frm.on_users()

    def on_yorg_init(self, msg):
        self.eng.log('yorg_init ' + str(msg['from']))
        usr = [user for user in self.eng.xmpp.users if user.name == str(msg['from'].bare)][0]
        usr.is_supporter = msg['body'] == '1'
        usr.is_in_yorg = True
        self.users_frm.on_users()

    def on_is_playing(self, msg):
        self.eng.log('is playing ' + str(msg['from']))
        users = [user for user in self.eng.xmpp.users if user.name == str(msg['from'].bare)]
        if not users: return  # when we get messages while we were offline
        usr = users[0]
        usr.is_playing = msg['body'] == '1'
        self.users_frm.on_users()

    def on_presence_available(self, msg):
        self.users_frm.on_users()

    def on_presence_available_room(self, msg):
        self.match_frm.on_presence_available_room(msg)
        self.msg_frm.on_presence_available_room(msg)

    def on_presence_unavailable_room(self, msg):
        if self.match_frm:
            self.match_frm.on_presence_unavailable_room(msg)
        self.msg_frm.on_presence_unavailable_room(msg)
        if str(msg['muc']['nick']) == self.users_frm.in_match_room:
            self.exit_dlg = ExitDialog(self.menu_args, msg)
            self.exit_dlg.attach(self.on_exit_dlg)
        if str(msg['muc']['nick']) == self.eng.xmpp.client.boundjid.bare and \
                self.match_frm and msg['muc']['room'] == self.match_frm.room:
            self.removed_dlg = RemovedDialog(self.menu_args, msg)
            self.removed_dlg.attach(self.on_remove_dlg)

    def on_exit_dlg(self):
        self.exit_dlg.destroy()
        self.notify('on_srv_quitted')
        #self.on_room_back()

    def on_remove_dlg(self):
        self.removed_dlg.destroy()
        self.notify('on_removed')
        self.on_room_back()

    def on_presence_unavailable(self, msg):
        self.users_frm.on_users()

    def on_start(self):
        self.eng.log('on_start')
        self.cancel_invites()
        self.users_frm.room_name = None
        self.match_frm.destroy()
        self.match_frm = None
        self.msg_frm.remove_groupchat()
        self.notify('on_start_match')

    def on_track_selected(self):
        self.match_frm.destroy()
        self.match_frm = None
        self.msg_frm.remove_groupchat()

    def on_room_back(self):
        if self.users_frm.room_name:  # i am the server:
            self.cancel_invites()
        if self.msg_frm.curr_match_room:  # if we've accepted the invitation
            self.eng.log('back (client)')
            self.eng.xmpp.client.plugin['xep_0045'].leaveMUC(
                self.msg_frm.curr_match_room, self.eng.xmpp.client.boundjid.bare)
            if self.match_frm:  # it's also invoked when server quits in car's page by os_srv_quitted
                self.match_frm.destroy()
                self.match_frm = None
                self.msg_frm.on_room_back()
        self.users_frm.invited_users = []
        self.users_frm.in_match_room = None
        self.users_frm.room_name = None
        for usr_name in [self.yorg_srv] + \
            [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=usr_name,
                mtype='ya2_yorg',
                msubject='is_playing',
                mbody='0')
        self.on_users()

    def cancel_invites(self):
        invited = self.users_frm.invited_users
        users = self.match_frm.users_names
        pending_users = [usr[2:] for usr in users if usr.startswith('? ')]
        self.eng.log('back (server): %s, %s, %s' % (invited, users, pending_users))
        for usr in pending_users:
            self.eng.log('cancel_invite ' + usr)
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=usr,
                mtype='ya2_yorg',
                msubject='cancel_invite',
                mbody='cancel_invite')

    def on_quit(self):
        if self.users_frm.room_name:  # i am the server:
            invited = self.users_frm.invited_users
            users = self.match_frm.users_names
            pending_users = [usr[2:] for usr in users if usr.startswith('? ')]
            self.eng.log('back (server): %s, %s, %s' % (invited, users, pending_users))
            for usr in pending_users:
                self.eng.log('cancel_invite ' + usr)
                self.eng.xmpp.client.send_message(
                    mfrom=self.eng.xmpp.client.boundjid.full,
                    mto=usr,
                    mtype='ya2_yorg',
                    msubject='cancel_invite',
                    mbody='cancel_invite')
        if self.msg_frm.curr_match_room:  # if we've accepted the invitation
            self.eng.log('back (client)')
            self.eng.xmpp.client.plugin['xep_0045'].leaveMUC(
                self.msg_frm.curr_match_room, self.eng.xmpp.client.boundjid.bare)
            if self.match_frm:  # it's also invoked when server quits in car's page by os_srv_quitted
                self.match_frm.destroy()
                self.match_frm = None
                self.msg_frm.on_room_back()
        self.users_frm.invited_users = []
        self.users_frm.in_match_room = None
        self.users_frm.room_name = None
        for usr_name in [self.yorg_srv] + \
            [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=usr_name,
                mtype='ya2_yorg',
                msubject='is_playing',
                mbody='0')
        self.on_users()

    def on_msg(self, msg):
        self.eng.log('received message')
        self.users_frm.set_size(False)
        self.msg_frm.show()
        self.msg_frm.on_msg(msg)

    def on_close_all_chats(self):
        self.eng.log('closed all chats')
        self.users_frm.set_size(True)
        self.msg_frm.hide()

    def on_groupchat_msg(self, msg):
        self.msg_frm.on_groupchat_msg(msg)

    def on_invite_chat(self, msg):
        if self.invite_dlg:  # we've already an invite
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=str(msg['from'].bare),
                msubject='declined',
                mtype='ya2_yorg',
                mbody=str(msg['body']))
            return
        self.invite_dlg = InviteDialog(self.menu_args, msg)
        self.invite_dlg.attach(self.on_invite_answer)
        for usr_name in [self.yorg_srv] + \
            [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=usr_name,
                mtype='ya2_yorg',
                msubject='is_playing',
                mbody='1')

    def on_invite_answer(self, msg, val):
        self.invite_dlg.detach(self.on_invite_answer)
        self.invite_dlg = self.invite_dlg.destroy()
        if val:
            self.users_frm.in_match_room = msg['from'].bare
            self.users_frm.on_users()
            chat, public_addr, local_addr = msg['body'].split('\n')
            for usr in self.eng.xmpp.users:
                if usr.name == msg['from'].bare:
                    usr.public_addr = public_addr
                    usr.local_addr = local_addr
            self.msg_frm.add_groupchat(chat, str(msg['from'].bare))
            self.eng.log('join to the chat ' + chat)
            self.eng.xmpp.client.plugin['xep_0045'].joinMUC(
                chat, self.eng.xmpp.client.boundjid.bare)
            room = chat
            nick = self.eng.xmpp.client.boundjid.bare
            self.create_match_frm(room, False)
            self.notify('on_create_room', room, nick)
            public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            sock = socket(AF_INET, SOCK_DGRAM)
            try:
                sock.connect(('ya2.it', 0))
                local_addr = sock.getsockname()[0]
            except gaierror:
                local_addr = ''
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=msg['from'].bare,
                mtype='ya2_yorg',
                msubject='ip_address',
                mbody=public_addr + '\n' + local_addr)
            for usr in self.eng.xmpp.users:
                if usr.name == msg['from'].bare:
                    if public_addr == usr.public_addr:
                        ip_addr = usr.local_addr
                    else:
                        ip_addr = usr.public_addr
            self.eng.client.start(self.process_msg_client, ip_addr)
        else:
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=str(msg['from'].bare),
                msubject='declined',
                mtype='ya2_yorg',
                mbody=str(msg['body']))
            for usr_name in [self.yorg_srv] + \
                [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
                self.eng.xmpp.client.send_message(
                    mfrom=self.eng.xmpp.client.boundjid.full,
                    mto=usr_name,
                    mtype='ya2_yorg',
                    msubject='is_playing',
                    mbody='1')

    def process_msg_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            self.eng.log_mgr.log('track selected: ' + data_lst[1])
            self.notify('on_start_match_client', data_lst[1])


    def on_declined(self, msg):
        self.eng.log('on declined')
        self.users_frm.on_declined(msg)
        self.match_frm.on_declined(msg)

    def on_ip_address(self, msg):
        self.eng.log('on ip address')
        public_addr, local_addr = msg['body'].split('\n')
        for usr in self.eng.xmpp.users:
            if usr.name == msg['from'].bare:
                usr.public_addr = public_addr
                usr.local_addr = local_addr

    def on_cancel_invite(self):
        self.invite_dlg.detach(self.on_invite_answer)
        self.invite_dlg = self.invite_dlg.destroy()

    def on_add_chat(self, usr):
        self.eng.log('on add chat' + str(usr))
        self.users_frm.set_size(False)
        self.msg_frm.show()
        self.msg_frm.add_chat(usr)

    def on_add_groupchat(self, room, usr):
        self.users_frm.set_size(False)
        self.msg_frm.show()
        self.msg_frm.add_groupchat(room, usr)
        self.match_frm.room = room
        self.notify('on_create_room', room, usr)

    def on_msg_focus(self, val):
        self.notify('on_msg_focus', val)

    def destroy(self):
        self.eng.log('multiplayer form: destroy')
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
