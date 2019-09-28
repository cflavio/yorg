from logging import info
from json import load
from socket import socket, AF_INET, SOCK_DGRAM, gaierror, error
from urllib.request import urlopen, URLError
from yyagl.gameobject import GameObject
from yyagl.engine.logic import VersionChecker
from menu.netmsgs import NetMsgs
from .usersfrm import UsersFrm
from .matchfrm import MatchFrmServer, MatchFrmServerClient
from .messagefrm import MessageFrm
from .friend_dlg import FriendDialog
from .server_dlg import ServerDialog
from .invite_dlg import InviteDialog
from .exit_dlg import ExitDialog
from .remove_dlg import RemovedDialog
#from .network_dlg import NetworkDialog


class MultiplayerFrm(GameObject):

    def __init__(self, menu_props, yorg_srv):
        GameObject.__init__(self)
        info('created multiplayer form')
        self.dialog = self.server_dlg = None
        self.invite_dlg = None
        self.yorg_srv = yorg_srv
        self.ver_check = VersionChecker()
        self.labels = []
        self.invited_users = []
        self.curr_inviting_usr = None
        self.menu_props = menu_props
        self.users_frm = UsersFrm(menu_props, yorg_srv)
        self.users_frm.attach(self.on_invite)
        self.users_frm.attach(self.on_add_chat)
        self.users_frm.attach(self.on_add_groupchat)
        self.msg_frm = MessageFrm(menu_props)
        self.msg_frm.attach(self.on_msg_focus)
        self.msg_frm.attach(self.on_close_all_chats)
        self.match_frm = None
        #self.match_frm.hide()
        self.msg_frm.hide()
        #self.eng.client.attach(self.on_presence_available)
        #self.eng.client.attach(self.on_presence_unavailable)
        #self.eng.client.attach(self.on_msg)
        #self.eng.client.attach(self.on_groupchat_msg)
        #self.eng.client.attach(self.on_is_playing)
        #self.eng.client.attach(self.on_invite)
        #self.eng.client.attach(self.on_invite_chat)
        #self.eng.client.attach(self.on_declined)
        #self.eng.client.attach(self.on_presence_available_room)
        #self.eng.client.attach(self.on_presence_unavailable_room)
        #self.eng.client.attach(self.on_rm_usr_from_match)

    def create_match_frm(self, room, is_server):
        cls = MatchFrmServer if is_server else MatchFrmServerClient
        self.match_frm = cls(self.menu_props)
        self.match_frm.attach(self.on_start)
        self.match_frm.show(room)

    def show(self):
        info('multiplayer form: show')
        self.users_frm.show()
        #self.match_frm.show()
        self.msg_frm.show()

    def hide(self):
        info('multiplayer form: hide')
        self.users_frm.hide()
        #self.match_frm.hide()
        self.msg_frm.hide()

    def on_user_subscribe(self, user):
        info('user subscribe: ' + str(user))
        if self.eng.xmpp.is_friend(user): return
        self.dialog = FriendDialog(self.menu_props, user)
        self.dialog.attach(self.on_friend_answer)

    def on_friend_answer(self, user, val):
        self.dialog.detach(self.on_friend_answer)
        self.dialog = self.dialog.destroy()
        info('send presence subscription to %s: %s' %(user, 'subscribed' if val else 'unsubscribed'))
        self.eng.xmpp.client.send_presence_subscription(
            pto=user,
            pfrom=self.eng.xmpp.client.boundjid.full,
            ptype='subscribed' if val else 'unsubscribed')
        self.on_users()

    def on_invite(self, usr):
        try:
            if not self.match_frm:
                self.eng.server.start(self.process_msg_srv, self.process_connection)
                self.create_match_frm('', True)
            self.match_frm.on_invite(usr)
        except (gaierror, URLError) as e:
            gaierror_str = _(
                "We've detected connection problems during server's creation. "
                "Please check your connection.")
            urlerror_str = _(
                "We can't connect to httpbin. Please retry later.")
            dct_msg = {gaierror: gaierror_str, URLError: urlerror_str}
            self.server_dlg = ServerDialog(self.menu_props, dct_msg[type(e)])
            self.server_dlg.attach(self.on_server_dlg)
            self.eng.server.stop()

    def on_server_dlg(self):
        self.server_dlg.detach(self.on_server_dlg)
        self.server_dlg = self.server_dlg.destroy()

    @staticmethod
    def process_msg_srv(data_lst):
        print(data_lst)

    def process_connection(self, client_address):
        info('connection from ' + client_address)

    def on_users(self): self.users_frm.on_users()

    def on_user_connected(self, user):
        info('user connected ' + user)
        self.users_frm.on_users()

    def on_user_disconnected(self, user):
        info('user disconnected ' + user)
        self.users_frm.on_users()

    def on_yorg_init(self, msg):
        info('yorg_init ' + str(msg['from']))
        usr = [user for user in self.eng.xmpp.users if user.name == str(msg['from'].bare)][0]
        usr.is_supporter = msg['body'] == '1'
        usr.is_in_yorg = True
        usr.is_playing = False
        self.users_frm.on_users()

    def on_is_playing(self, uid, is_playing):
        info('is playing %s %s' % (uid, is_playing))
        users = [user for user in self.eng.client.users if user.uid == uid]
        #if not users: return  # when we get messages while we were offline
        usr = users[0]
        usr.is_playing = is_playing
        self.users_frm.on_users()

    def on_presence_available(self, msg):
        self.users_frm.on_users()

    def on_presence_available_room(self, uid, room):
        if self.match_frm:  # if the client accepted after server's start
            self.match_frm.on_presence_available_room(uid, room)
        self.msg_frm.on_presence_available_room(uid, room)

    def on_presence_unavailable_room(self, uid, room_name):
        if self.match_frm:
            self.match_frm.on_presence_unavailable_room(uid, room_name)
        self.msg_frm.on_presence_unavailable_room(uid, room_name)
        if uid == self.users_frm.in_match_room:
            #self.eng.xmpp.notify('on_server_quit')
            self.exit_dlg = ExitDialog(self.menu_props, uid)
            self.exit_dlg.attach(self.on_exit_dlg)
            self.eng.show_cursor()
        if uid == self.eng.client.myid and \
                self.match_frm and room_name == self.match_frm.room:
            self.removed_dlg = RemovedDialog(self.menu_props)
            self.removed_dlg.attach(self.on_remove_dlg)

    def on_rm_usr_from_match(self, data_lst):
        if self.match_frm:  # if the user has already accepted
            self.match_frm.on_rm_usr_from_match(data_lst)
            self.msg_frm.match_msg_frm.on_rm_usr_from_match(data_lst[0])
        if data_lst[0] == self.eng.client.myid and \
                self.match_frm and data_lst[1] == self.match_frm.room:
            self.removed_dlg = RemovedDialog(self.menu_props)
            self.removed_dlg.attach(self.on_remove_dlg)
        elif data_lst[0] == self.eng.client.myid and \
                not self.match_frm and self.invite_dlg:
            self.invite_dlg.detach(self.on_invite_answer)
            self.invite_dlg = self.invite_dlg.destroy()
            self.users_frm.invited = False

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
        if msg == str(self.curr_inviting_usr):
            self.on_cancel_invite()

    def on_logout(self):
        self.users_frm.on_logout()

    def on_start(self):
        info('on_start')
        self.cancel_invites()
        self.users_frm.room_name = None
        self.match_frm.destroy()
        self.match_frm = None
        self.msg_frm.remove_groupchat()
        self.notify('on_start_match')
        self.users_frm.set_size(False)
        self.msg_frm.show()

    def on_track_selected(self):
        #self.match_frm.destroy()
        self.match_frm = None
        #self.msg_frm.remove_groupchat()

    def on_room_back(self):
        if self.users_frm.room_name:  # i am the server:
            self.cancel_invites()
        if self.msg_frm.curr_match_room:  # if we've accepted the invitation
            info('back (client)')
            #self.eng.xmpp.client.plugin['xep_0045'].leaveMUC(
            #    self.msg_frm.curr_match_room, self.eng.xmpp.client.boundjid.bare)
            self.eng.client.is_server_active = False
            self.eng.client.is_client_active = False
            self.eng.client.register_rpc('leave_room')
            self.eng.client.leave_room(self.msg_frm.curr_match_room)
            if self.match_frm:  # it's also invoked when server quits in car's page by os_srv_quitted
                self.match_frm.destroy()
                self.match_frm = None
                self.msg_frm.on_room_back()
        self.users_frm.invited_users = []
        self.users_frm.in_match_room = None
        self.users_frm.room_name = None
        #for usr_name in [self.yorg_srv] + \
        #    [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
        #    self.eng.xmpp.client.send_message(
        #        mfrom=self.eng.xmpp.client.boundjid.full,
        #        mto=usr_name,
        #        mtype='ya2_yorg',
        #        msubject='is_playing',
        #        mbody='0')
        self.on_users()
        self.msg_frm.curr_match_room = None

    def send_is_playing(self, value):
        for usr_name in [self.yorg_srv] + \
            [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            self.eng.xmpp.client.send_message(
                mfrom=self.eng.xmpp.client.boundjid.full,
                mto=usr_name,
                mtype='ya2_yorg',
                msubject='is_playing',
                mbody='1' if value else '0')

    def cancel_invites(self):
        invited = self.users_frm.invited_users
        users = self.match_frm.users_names
        pending_users = [usr[2:] for usr in users if usr.startswith('? ')]
        info('cancel invites: %s, %s, %s' % (invited, users, pending_users))
        for usr in pending_users:
            info('cancel_invite %s %s' % (usr, self.match_frm.room))
            self.eng.client.register_rpc('rm_usr_from_match')
            self.eng.client.rm_usr_from_match(usr, self.match_frm.room)

    def on_quit(self):
        if self.eng.server.is_active: self.eng.server.stop()
        if self.users_frm.room_name:  # i am the server:
            invited = self.users_frm.invited_users
            users = self.match_frm.users_names
            pending_users = [usr[2:] for usr in users if usr.startswith('? ')]
            info('quit (server): %s, %s, %s' % (invited, users, pending_users))
            for usr in pending_users:
                info('cancel_invite ' + usr)
                self.eng.xmpp.client.send_message(
                    mfrom=self.eng.xmpp.client.boundjid.full,
                    mto=usr,
                    mtype='ya2_yorg',
                    msubject='cancel_invite',
                    mbody='cancel_invite')
        if self.msg_frm.curr_match_room:  # if we've accepted the invitation
            info('back (client)')
            #self.eng.xmpp.client.plugin['xep_0045'].leaveMUC(
            #    self.msg_frm.curr_match_room, self.eng.xmpp.client.boundjid.bare)
            self.eng.client.is_server_active = False
            self.eng.client.is_client_active = False
            self.eng.client.register_rpc('leave_room')
            self.eng.client.leave_room(self.msg_frm.curr_match_room)
            if self.match_frm:  # it's also invoked when server quits in car's page by on_srv_quitted
                self.match_frm.destroy()
                self.match_frm = None
                self.msg_frm.on_room_back()
        self.users_frm.invited_users = []
        self.users_frm.in_match_room = None
        self.users_frm.room_name = None
        #for usr_name in [self.yorg_srv] + \
        #    [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
        #    self.eng.xmpp.client.send_message(
        #        mfrom=self.eng.xmpp.client.boundjid.full,
        #        mto=usr_name,
        #        mtype='ya2_yorg',
        #        msubject='is_playing',
        #        mbody='0')
        self.on_users()
        self.msg_frm.curr_match_room = None

    def on_msg(self, msg):
        info('received message')
        self.users_frm.set_size(False)
        self.msg_frm.show()
        self.msg_frm.on_msg(*msg)

    def on_close_all_chats(self):
        info('closed all chats')
        self.users_frm.set_size(True)
        self.msg_frm.hide()

    def on_groupchat_msg(self, from_, to, txt):
        self.msg_frm.on_groupchat_msg(from_, to, txt)

    def on_invite_chat(self, from_, to, roomname):
        #if self.invite_dlg or self.match_frm:  # we've already an invite
        #    self.eng.xmpp.client.send_message(
        #        mfrom=self.eng.xmpp.client.boundjid.full,
        #        mto=str(msg['from'].bare),
        #        msubject='declined',
        #        mtype='ya2_yorg',
        #        mbody=str(msg['body']))
        #    return
        self.invite_dlg = InviteDialog(self.menu_props, from_, roomname)
        self.invite_dlg.attach(self.on_invite_answer)
        self.curr_inviting_usr = from_
        #for usr_name in [self.yorg_srv] + \
        #    [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
        #    self.eng.xmpp.client.send_message(
        #        mfrom=self.eng.xmpp.client.boundjid.full,
        #        mto=usr_name,
        #        mtype='ya2_yorg',
        #        msubject='is_playing',
        #        mbody='1')
        self.users_frm.invited = True
        self.on_users()

    def on_invite_answer(self, from_, roomname, val):
        self.curr_inviting_usr = None
        self.invite_dlg.detach(self.on_invite_answer)
        self.invite_dlg = self.invite_dlg.destroy()
        self.users_frm.invited = False
        if val:
            #mypublic_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            #sock = socket(AF_INET, SOCK_DGRAM)
            #try:
            #    sock.connect(('ya2.it', 8080))
            #    mylocal_addr = sock.getsockname()[0]
            #except gaierror:
            #    mylocal_addr = ''
            #self.eng.xmpp.client.send_message(
            #    mfrom=self.eng.xmpp.client.boundjid.full,
            #    mto=msg['from'].bare,
            #    mtype='ya2_yorg',
            #    msubject='ip_address',
            #    mbody=mypublic_addr + '\n' + mylocal_addr)
            #chat, public_addr, local_addr = msg['body'].split('\n')
            #for usr in self.eng.xmpp.users:
            #    if usr.name == msg['from'].bare:
            #        usr.public_addr = public_addr
            #        usr.local_addr = local_addr
            #for usr in self.eng.xmpp.users:
            #    if usr.name == msg['from'].bare:
            #        if mypublic_addr == usr.public_addr:
            #            ip_addr = usr.local_addr
            #            my_addr = mylocal_addr
            #        else:
            #            ip_addr = usr.public_addr
            #            my_addr = mypublic_addr
            #try: self.eng.client.start(self.process_msg_client, ip_addr, my_addr)
            #except (NetworkError, error) as exc:
            #    self.network_dlg = NetworkDialog(self.menu_props)
            #    self.network_dlg.attach(self.on_network_dlg)
            #    return
            self.users_frm.in_match_room = from_
            self.users_frm.on_users()
            self.msg_frm.add_groupchat(roomname, from_)
            info('join to the chat ' + roomname)
            #self.eng.xmpp.client.plugin['xep_0045'].joinMUC(
            #    chat, self.eng.xmpp.client.boundjid.bare)
            self.eng.client.register_rpc('join_room')
            self.eng.client.join_room(roomname)
            self.eng.client.is_client_active = True
            nick = self.eng.client.myid
            self.create_match_frm(roomname, False)
            self.notify('on_create_room', roomname, nick)
            self.eng.client.attach(self.on_track_selected_msg)
        else:
            self.eng.client.send(['declined', self.eng.client.myid, from_])
            #self.eng.xmpp.client.send_message(
            #    mfrom=self.eng.xmpp.client.boundjid.full,
            #    mto=str(msg['from'].bare),
            #    msubject='declined',
            #    mtype='ya2_yorg',
            #    mbody=str(msg['body']))
            #for usr_name in [self.yorg_srv] + \
            #    [_usr.name_full for _usr in self.eng.xmpp.users if _usr.is_in_yorg]:
            #    self.eng.xmpp.client.send_message(
            #        mfrom=self.eng.xmpp.client.boundjid.full,
            #        mto=usr_name,
            #        mtype='ya2_yorg',
            #        msubject='is_playing',
            #        mbody='1')

    def process_msg_client(self, data_lst, sender):
        pass
        #if data_lst[0] == NetMsgs.track_selected:
        #    self.eng.log_mgr.log('track selected: ' + data_lst[1])
        #    self.notify('on_start_match_client', data_lst[1])
        #    self.users_frm.set_size(False)
        #    self.msg_frm.show()

    def on_track_selected_msg(self, track):
        pass
        #self.eng.log_mgr.log('track selected: ' + track)
        #self.eng.client.detach(self.on_track_selected_msg)
        #self.notify('on_start_match_client', track)
        #self.users_frm.set_size(False)
        #self.msg_frm.show()

    def on_declined(self, msg):
        info('on declined')
        self.users_frm.on_declined(msg)
        self.match_frm.on_declined(msg)
        self.msg_frm.match_msg_frm.update_title()

    def on_ip_address(self, msg):
        info('on ip address')
        public_addr, local_addr = msg['body'].split('\n')
        for usr in self.eng.xmpp.users:
            if usr.name == msg['from'].bare:
                usr.public_addr = public_addr
                usr.local_addr = local_addr

    #def on_network_dlg(self):
    #    self.network_dlg.destroy()

    def on_cancel_invite(self):
        self.curr_inviting_usr = None
        if self.invite_dlg:  # the client accepted but the server started
            self.invite_dlg.detach(self.on_invite_answer)
            self.invite_dlg = self.invite_dlg.destroy()
        self.users_frm.invited = False
        self.on_users()

    def on_add_chat(self, usr):
        info('on add chat' + str(usr))
        self.users_frm.set_size(False)
        self.msg_frm.show()
        self.msg_frm.add_chat(usr)

    def on_add_groupchat(self, room, usr):
        if self.match_frm.room == room: return
        self.msg_frm.add_groupchat(room, usr)
        self.match_frm.room = room
        self.notify('on_create_room', room, usr)

    def on_msg_focus(self, val):
        self.notify('on_msg_focus', val)

    def destroy(self):
        info('multiplayer form: destroy')
        self.frm = self.frm.destroy()
        GameObject.destroy(self)
