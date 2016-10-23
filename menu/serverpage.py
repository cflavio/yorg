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

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('ya2.it', 0))
        local_addr = sock.getsockname()[0]
        public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
        addr = local_addr + ' - ' + public_addr
        txt = OnscreenText(text=addr, scale=.12, pos=(0, .4),
                           font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [self.conn_txt]
        btn = DirectButton(
            text=_('Start'), scale=.2, pos=(0, 1, -.5),
            text_fg=(.75, .75, .75, 1),
            text_font=menu_gui.font, frameColor=menu_args.btn_color,
            command=lambda: self.menu.logic.push_page(TrackPage(self.menu)),
            frameSize=menu_args.btn_size,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
        self.widgets += [btn]
        PageGui.build(self)
        eng.server.start(self.process_msg, self.process_connection)

    @staticmethod
    def process_msg(data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log_mgr.log('connection from ' + client_address)
        self.conn_txt.setText(_('connection from ') + client_address)


class ServerPage(Page):
    gui_cls = ServerPageGui
