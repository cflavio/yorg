from logging import info
from time import strftime
from yyagl.engine.gui.page import Page, PageFacade, PageEvent
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from .multiplayer.matchfrm import MatchFrmServer, MatchFrmServerClient
from .multiplayer.messagefrm import MatchMsgFrm
from .multiplayer.exit_dlg import ExitDialog

class RoomPageGui(ThanksPageGui):

    frm_cls = MatchFrmServer

    def __init__(self, mediator, menu_props, room_name, srv_usr):
        self.menu_props = menu_props
        if not room_name:
            room_name = self.eng.client.myid + strftime('%y%m%d%H%M%S')
        self.room_name = room_name
        self.srv_usr = srv_usr
        self.match_frm = self.frm_cls(menu_props, room_name)
        self.match_msg_frm = MatchMsgFrm(self.menu_props)
        ThanksPageGui.__init__(self, mediator, menu_props)
        self.eng.client.register_rpc('join_room')
        self.eng.client.join_room(room_name)
        info('created room ' + room_name)
        self.eng.client.is_server_active = True
        self.eng.client.attach(self.on_presence_available_room)
        self.eng.client.attach(self.on_presence_unavailable_room)
        self.match_frm.attach(self.on_start)
        self.match_msg_frm.add_groupchat(room_name)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        self.add_widgets(self.match_frm.widgets + self.match_msg_frm.widgets)
        ThanksPageGui.build(self)

    def on_presence_available_room(self, uid, room):
        self.match_frm.on_presence_available_room(uid, room)

    def on_presence_unavailable_room(self, uid, room):
        self.match_frm.on_presence_unavailable_room(uid, room)

    def on_start(self):
        self.eng.client.send(['room_start'])
        self.notify('on_start_match', self.room_name)

    def destroy(self):
        self.eng.client.detach(self.on_presence_available_room)
        self.eng.client.detach(self.on_presence_unavailable_room)
        self.match_frm.detach(self.on_start)
        self.match_frm.destroy()
        self.match_msg_frm.destroy()
        ThanksPageGui.destroy(self)


class RoomPageClientGui(RoomPageGui):

    frm_cls = MatchFrmServerClient

    def __init__(self, mediator, menu_props, room_name, srv_usr):
        RoomPageGui.__init__(self, mediator, menu_props, room_name, srv_usr)
        self.eng.client.attach(self.on_track_selected_msg)

    def on_presence_unavailable_room(self, uid, room):
        RoomPageGui.on_presence_unavailable_room(self, uid, room)
        if uid == self.srv_usr:
            self.exit_dlg = ExitDialog(self.menu_props, uid)
            self.exit_dlg.attach(self.on_exit_dlg)
            self.eng.show_cursor()

    def on_exit_dlg(self):
        if self.eng.client.observing(self.on_track_selected_msg):
            self.eng.client.detach(self.on_track_selected_msg)
        self.exit_dlg.destroy()
        self.notify('on_srv_quitted')

    def on_track_selected_msg(self, track):
        info('track selected (room page): ' + track)
        self.eng.client.detach(self.on_track_selected_msg)
        self.notify('on_start_match_client_page', track, self.room_name)


class RoomPageEvent(PageEvent):

    def __init__(self, mdt, room):
        PageEvent.__init__(self, mdt)
        self.room = room

    def on_back(self):
        info('RoomPageEvent::on_back')
        self.eng.client.is_server_active = False
        self.eng.client.is_client_active = False
        self.eng.client.register_rpc('leave_room')
        self.eng.client.leave_room(self.room)


class RoomPage(Page):
    gui_cls = RoomPageGui
    event_cls = RoomPageEvent

    def __init__(self, menu_props, room, nick, uid_srv):
        self.menu_props = menu_props
        self.room = room
        self.uid_srv = uid_srv
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self, self.room])],
        [('gui', self.gui_cls, [self, self.menu_props, self.room, self.uid_srv])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)



class RoomPageClient(RoomPage):
    gui_cls = RoomPageClientGui
