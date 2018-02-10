from socket import socket, AF_INET, SOCK_DGRAM, gaierror
from json import load
from urllib2 import urlopen
from yyagl.library.gui import Btn
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageEvent, PageFacade
from yyagl.gameobject import GameObject
from yyagl.engine.network.network import NetworkError
from .thankspage import ThanksPageGui


class ServerEvent(PageEvent):

    def on_back(self):
        if self.eng.server.is_active:
            self.eng.server.destroy()

    @staticmethod
    def process_msg(data_lst):
        print data_lst

    def process_connection(self, client_address):
        self.eng.log_mgr.log('connection from ' + client_address)
        self.mediator.gui.conn_txt.setText(_('connection from ') + client_address)


class ServerPageGui(ThanksPageGui):

    def __init__(self, mediator, serverpage_props):
        self.conn_txt = None
        self.props = serverpage_props
        ThanksPageGui.__init__(self, mediator, serverpage_props.gameprops.menu_args)

    def build(self):
        menu_args = self.props.gameprops.menu_args
        sock = socket(AF_INET, SOCK_DGRAM)
        try:
            sock.connect(('ya2.it', 0))
            local_addr = sock.getsockname()[0]
            public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
            addr = local_addr + ' - ' + public_addr
            self.add_widgets([OnscreenText(
                text=addr, scale=.12, pos=(0, .4), font=menu_args.font,
                fg=menu_args.text_active)])
        except gaierror:
            self.eng.log_mgr.log('no connection')
        self.conn_txt = OnscreenText(
            scale=.12, pos=(0, .2), font=menu_args.font,
            fg=menu_args.text_active)
        self.add_widgets([self.conn_txt])
        scb = lambda: self.notify('on_push_page', 'trackpageserver',
                                  [self.props])
        start_btn = Btn(
            text=_('Start'), pos=(0, 1, -.5), command=scb,
            **menu_args.btn_args)
        self.add_widgets([start_btn])
        ThanksPageGui.build(self)
        evt = self.mediator.event
        try:
            self.eng.server.start(evt.process_msg, evt.process_connection)
        except NetworkError:
            txt = OnscreenText(_('Error'), pos=(0, -.05), fg=(1, 0, 0, 1),
                               scale=.16, font=menu_args.font)
            start_btn.disable()
            self.eng.do_later(5, txt.destroy)


class ServerPage(Page):
    gui_cls = ServerPageGui
    event_cls = ServerEvent

    def __init__(self, serverpage_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, serverpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
