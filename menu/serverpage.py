from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from json import load
from urllib2 import urlopen
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageEvent
from yyagl.engine.network.server import Server
from yyagl.gameobject import GameObject
from .trackpage import TrackPageServer, TrackPageProps
from .thankspage import ThanksPageGui


class ServerPageProps(object):

    def __init__(self, cars, car_path, phys_path, tracks, tracks_tr, track_img,
                 player_name, drivers_img, cars_img, drivers):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.drivers = drivers


class ServerEvent(PageEvent):

    def on_back(self):
        if Server().is_active:
            Server().destroy()

    @staticmethod
    def process_msg(data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log('connection from ' + client_address)
        self.mdt.gui.conn_txt.setText(_('connection from ') + client_address)


class ServerPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, serverpage_props, menu):
        self.conn_txt = None
        self.menu = menu
        self.props = serverpage_props
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
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
            eng.log('no connection')
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_args.font, fg=menu_args.text_fg)
        self.add_widget(self.conn_txt)
        tp_props = TrackPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.add_widget(DirectButton(
            text=_('Start'), pos=(0, 1, -.5),
            command=lambda: self.menu.push_page(TrackPageServer(self.menu,
                                                                tp_props)),
            **menu_gui.menu_args.btn_args))
        ThanksPageGui.bld_page(self)
        evt = self.mdt.event
        Server().start(evt.process_msg, evt.process_connection)


class ServerPage(Page):
    gui_cls = ServerPageGui
    event_cls = ServerEvent

    def __init__(self, menu_args, serverpage_props, menu):
        self.menu_args = menu_args
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, serverpage_props,
                                    self.menu])]]
        GameObject.__init__(self, init_lst)
