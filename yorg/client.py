from socket import error
from yyagl.gameobject import GameObject


class User(object):

    def __init__(self, uid, is_supporter, is_playing):
        self.uid = uid
        self.is_supporter = is_supporter
        self.is_playing = is_playing


class YorgClient(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.authenticated = False
        self.is_server_up = True
        try: self.is_server_up = self.eng.client.start(self.on_msg, self.eng.cfg.dev_cfg.server)
        except error: self.is_server_up = False
        self.users = []
        self.is_server_active = False
        self.is_client_active = False

    def start(self, uid):
        self.myid = uid
        self.eng.client.register_rpc('get_users')
        users = self.eng.client.get_users()
        self.users = [User(*args) for args in users]

    def on_msg(self, data_lst, sender):
        if data_lst[0] == 'login':
            self.users += [User(*data_lst[1:])]
            self.notify('on_presence_available', data_lst[1:])
            self.eng.log('login %s' % data_lst[1])
        if data_lst[0] == 'logout':
            for usr in self.users[:]:
                if usr.uid == data_lst[1]:
                    self.users.remove(usr)
                    self.eng.log('logout %s' % data_lst[1])
            self.notify('on_presence_unavailable', data_lst[1:])
        if data_lst[0] == 'msg':
            self.notify('on_msg', data_lst[1:])
        if data_lst[0] == 'msg_room':
            self.notify('on_groupchat_msg', data_lst[1], data_lst[2], data_lst[3])
        if data_lst[0] == 'is_playing':
            self.notify('on_is_playing', data_lst[1], data_lst[2])
        if data_lst[0] == 'invite_chat':
            self.notify('on_invite_chat', data_lst[1], data_lst[2], data_lst[3])
        if data_lst[0] == 'declined':
            self.notify('on_declined', data_lst[1])
        if data_lst[0] == 'presence_available_room':
            self.notify('on_presence_available_room', data_lst[1], data_lst[2])
        if data_lst[0] == 'presence_unavailable_room':
            self.notify('on_presence_unavailable_room', data_lst[1], data_lst[2])
        if data_lst[0] == 'track_selected':
            self.notify('on_track_selected_msg', data_lst[1])
        if data_lst[0] == 'car_selection':
            self.notify('on_car_selection', data_lst[1:])
        if data_lst[0] == 'car_deselection':
            self.notify('on_car_deselection', data_lst[1:])
        if data_lst[0] == 'drv_selection':
            self.notify('on_drv_selection', data_lst[1:])
        if data_lst[0] == 'drv_deselection':
            self.notify('on_drv_deselection', data_lst[1:])
        if data_lst[0] == 'start_drivers':
            self.notify('on_start_drivers', data_lst[1:])
        if data_lst[0] == 'start_race':
            self.notify('on_start_race', data_lst[1:])
        if data_lst[0] == 'begin_race':
            self.notify('on_begin_race')
        if data_lst[0] == 'start_countdown':
            self.notify('on_start_countdown')
        if data_lst[0] == 'player_info':
            self.notify('on_player_info', data_lst[1:])
        if data_lst[0] == 'game_packet':
            self.notify('on_game_packet', data_lst[1:])
        if data_lst[0] == 'end_race_player':
            self.notify('on_end_race_player', data_lst[1])

    def find_usr(self, uid):
        return [usr for usr in self.users if usr.uid == uid][0]

    @property
    def users_nodup(self):
        return self.users
