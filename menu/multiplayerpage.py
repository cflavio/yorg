from keyring import get_password, set_password, set_keyring
#from keyring_jeepney import Keyring
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class MultiplayerPageGui(ThanksPageGui):

    def __init__(self, mdt, mp_props):
        self.props = mp_props
        options = self.props.opt_file
        if options['settings']['xmpp']['usr'] and options['settings']['xmpp']['pwd']:
        #if options['settings']['xmpp']['usr']:
            #if platform.startswith('linux'): set_keyring(Keyring())
            #pwd = get_password('ya2_rog', options['settings']['xmpp']['usr'])
            #if not pwd:
                pwd = options['settings']['xmpp']['pwd']
                #set_password('ya2_rog', options['settings']['xmpp']['usr'], pwd)
            #self.eng.xmpp.start(options['settings']['xmpp']['usr'], pwd)
                self.eng.xmpp.start(options['settings']['xmpp']['usr'], pwd, self.on_ok, self.on_ko)
        ThanksPageGui.__init__(self, mdt, mp_props.gameprops.menu_args)
        if not (options['settings']['xmpp']['usr'] and options['settings']['xmpp']['pwd']):
            self.on_ko()

    def show(self):
        ThanksPageGui.show(self)
        self.rebuild_page()

    def on_ok(self):
        self.connected = True
        self.rebuild_page()

    def on_ko(self):
        self.connected = False
        self.rebuild_page()

    def on_logout(self):
        self.eng.xmpp.destroy()
        options = self.props.opt_file
        options['settings']['xmpp']['usr'] = ''
        options['settings']['xmpp']['pwd'] = ''
        options.store()
        self._on_back()

    def rebuild_page(self):
        if self.connected or self.eng.xmpp.xmpp and self.eng.xmpp.xmpp.authenticated:
            scb = lambda: self.notify('on_push_page', 'server', [self.props])
            ccb = lambda: self.notify('on_push_page', 'client', [self.props])
            menu_data = [
                ('Server', scb),
                ('Client', ccb),
                (_('Log-out'), self.on_logout)]
            widgets = [
                DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                             **self.props.gameprops.menu_args.btn_args)
                for i, menu in enumerate(menu_data)]
        else:
            menu_data = [
                (_('Log-in'), self.on_login)]
            widgets = [
                DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                             **self.props.gameprops.menu_args.btn_args)
                for i, menu in enumerate(menu_data)]
        map(self.add_widget, widgets)

    def on_login(self):
        self.transition_exit()
        self.widgets = []
        self.notify('on_push_page', 'login', [self.props])

    def bld_page(self):
        ThanksPageGui.bld_page(self)


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui

    def __init__(self, mp_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, mp_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
