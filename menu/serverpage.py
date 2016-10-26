from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.page import Page, PageGui
from .trackpage import TrackPage
import socket
from json import load
from urllib2 import urlopen


class ServerPageGui(PageGui):

    def __init__(self, mdt, menu):
        self.conn_txt = None
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('ya2.it', 0))
        local_addr = sock.getsockname()[0]
        public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
        addr = local_addr + ' - ' + public_addr
        txt = OnscreenText(text=addr, scale=.12, pos=(0, .4),
                           font=menu_gui.font, fg=menu_args.text_fg)
        self.widgets += [txt]
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_gui.font, fg=menu_args.text_fg)
        self.widgets += [self.conn_txt]
        btn = DirectButton(
            text=_('Start'), pos=(0, 1, -.5),
            command=lambda: self.menu.logic.push_page(TrackPage(self.menu)),
            **menu_gui.btn_args)
        self.widgets += [btn]
        PageGui.build_page(self)
        eng.server.start(self.process_msg, self.process_connection)
        # stop the server on back

    @staticmethod
    def process_msg(data_lst):
        # into event
        print data_lst

    def process_connection(self, client_address):
        # into event
        eng.log_mgr.log('connection from ' + client_address)
        self.conn_txt.setText(_('connection from ') + client_address)


class ServerPage(Page):
    gui_cls = ServerPageGui
