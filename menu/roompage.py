from time import strftime
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from multiplayer.matchfrm import MatchFrmServer, MatchFrmServerClient
from multiplayer.messagefrm import MatchMsgFrm


class RoomPageGui(ThanksPageGui):

    frm_cls = MatchFrmServer

    def __init__(self, mediator, menu_props, room_name=None):
        self.menu_props = menu_props
        ThanksPageGui.__init__(self, mediator, menu_props)
        if not room_name:
            room_name = self.eng.client.myid + strftime('%y%m%d%H%M%S')
        self.match_frm = self.frm_cls(menu_props, room_name)
        self.match_msg_frm = MatchMsgFrm(self.menu_props)
        self.eng.client.register_rpc('join_room')
        self.eng.client.join_room(room_name)
        self.eng.log('created room ' + room_name)
        self.eng.client.is_server_active = True
        self.eng.client.attach(self.on_presence_available_room)
        self.match_frm.attach(self.on_start)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        widgets = []
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def on_presence_available_room(self, uid, room):
        self.match_frm.on_presence_available_room(uid, room)

    def on_start(self):
        self.eng.client.send(['room_start'])
        self.notify('on_start_match')

    def destroy(self):
        self.match_frm.destroy()
        self.match_msg_frm.destroy()


class RoomPageClientGui(RoomPageGui):

    frm_cls = MatchFrmServerClient

    def __init__(self, mediator, menu_props, room_name):
        RoomPageGui.__init__(self, mediator, menu_props, room_name)
        self.eng.client.attach(self.on_track_selected_msg)

    def on_track_selected_msg(self, track):
        self.eng.log_mgr.log('track selected: ' + track)
        self.eng.client.detach(self.on_track_selected_msg)
        self.notify('on_start_match_client_page', track)


class RoomPage(Page):
    gui_cls = RoomPageGui

    def __init__(self, menu_props, room, nick):
        self.menu_props = menu_props
        self.room = room
        self.nick = nick
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.menu_props, self.room])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)



class RoomPageClient(RoomPage):
    gui_cls = RoomPageClientGui
