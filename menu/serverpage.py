from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.page import Page, PageEvent, PageGui
from trackpage import TrackPage


class ServerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('ya2.it', 0))
        local_addr = s.getsockname()[0]
        from json import load
        from urllib2 import urlopen
        public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
        addr = local_addr + ' - ' + public_addr
        self.widgets += [
            OnscreenText(text=addr, scale=.12, pos=(0, .4),
                         font=menu_gui.font, fg=(.75, .75, .75, 1))]
        self.conn_txt = OnscreenText(scale=.12,
                         pos=(0, .2), font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [self.conn_txt]
        self.widgets += [
            DirectButton(
                text=_('Start'), scale=.2, pos=(0, 1, -.5),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=lambda: self.menu.logic.push_page(TrackPage(self.menu)),
                frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        PageGui.build(self)
        eng.server.start(self.process_msg, self.process_connection)

    def process_msg(self, data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log_mgr.log('connection from ' + client_address)
        self.conn_txt.setText(_('connection from ') + client_address)


class ServerPage(Page):
    '''This class models a page.'''
    gui_cls = ServerPageGui
