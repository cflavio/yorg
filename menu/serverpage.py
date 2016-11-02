from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.page import Page, PageGui, PageEvent
from .trackpage import TrackPageServer
import socket
from json import load
from urllib2 import urlopen


class ServerEvent(PageEvent):

    def on_back(self):
        if eng.server.is_active:
            eng.server.stop()

    @staticmethod
    def process_msg(data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log_mgr.log('connection from ' + client_address)
        self.mdt.gui.conn_txt.setText(_('connection from ') + client_address)


class ServerPageGui(PageGui):

    def __init__(self, mdt, menu):
        self.conn_txt = None
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(('ya2.it', 0))
            local_addr = sock.getsockname()[0]
            public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            addr = local_addr + ' - ' + public_addr
            txt = OnscreenText(text=addr, scale=.12, pos=(0, .4),
                               font=menu_gui.font, fg=menu_args.text_fg)
            self.widgets += [txt]
        except socket.gaierror:
            eng.log_mgr.log('no connection')
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_gui.font, fg=menu_args.text_fg)
        self.widgets += [self.conn_txt]
        push = self.menu.logic.push_page
        btn = DirectButton(
            text=_('Start'), pos=(0, 1, -.5),
            command=lambda: push(TrackPageServer(self.menu)),
            **menu_gui.btn_args)
        self.widgets += [btn]
        PageGui.build_page(self)
        evt = self.mdt.event
        eng.server.start(evt.process_msg, evt.process_connection)


class ServerPage(Page):
    gui_cls = ServerPageGui
    event_cls = ServerEvent

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_event, 'ServerEvent')],
            [(self.build_gui, 'ServerPageGui', [self.menu])],
            [(self.build_logic, 'Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')]]
