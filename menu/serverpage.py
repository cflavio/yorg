from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from json import load
from urllib2 import urlopen
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui, PageEvent
from yyagl.gameobject import GameObjectMdt
from .trackpage import TrackPageServer
from .thankspage import ThanksPageGui


class ServerEvent(PageEvent):

    def on_back(self):
        if eng.is_server_active:
            eng.destroy_server()

    @staticmethod
    def process_msg(data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log('connection from ' + client_address)
        self.mdt.gui.conn_txt.setText(_('connection from ') + client_address)


class ServerPageGui(ThanksPageGui):

    def __init__(self, mdt, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img, player_name, drivers_img, cars_img):
        self.conn_txt = None
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        ThanksPageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        sock = socket(AF_INET, SOCK_DGRAM)
        try:
            sock.connect(('ya2.it', 0))
            local_addr = sock.getsockname()[0]
            public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            addr = local_addr + ' - ' + public_addr
            self.add_widget(OnscreenText(
                text=addr, scale=.12, pos=(0, .4), font=menu_args.font,
                fg=menu_args.text_fg))
        except gaierror:
            eng.log_mgr.log('no connection')
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_args.font, fg=menu_args.text_fg)
        self.add_widget(self.conn_txt)
        push = self.menu.logic.push_page
        self.add_widget(DirectButton(
            text=_('Start'), pos=(0, 1, -.5),
            command=lambda: push(TrackPageServer(
                self.menu, self.cars, self.car_path, self.phys_path,
                self.tracks, self.tracks_tr, self.track_img, self.player_name,
                self.drivers_img, self.cars_img)),
            **menu_gui.btn_args))
        ThanksPageGui.build_page(self)
        evt = self.mdt.event
        eng.server.start(evt.process_msg, evt.process_connection)


class ServerPage(Page):
    gui_cls = ServerPageGui
    event_cls = ServerEvent

    def __init__(self, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img, player_name, drivers_img, cars_img):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [
                self, self.menu, cars, car_path, phys_path, tracks, tracks_tr,
                track_img, player_name, drivers_img, cars_img])]]
        GameObjectMdt.__init__(self, init_lst)
