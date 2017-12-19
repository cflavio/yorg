from keyring import get_password, set_password, set_keyring
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class MultiplayerPageGui(ThanksPageGui):

    def __init__(self, mdt, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mdt, mp_props.gameprops.menu_args)

    def show(self):
        ThanksPageGui.show(self)
        self.bld_page()

    def on_logout(self):
        self.eng.xmpp.destroy()
        options = self.props.opt_file
        options['settings']['xmpp']['usr'] = ''
        options['settings']['xmpp']['pwd'] = ''
        options.store()
        self._on_back()

    def bld_page(self):
        if self.eng.xmpp.xmpp and self.eng.xmpp.xmpp.authenticated:
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
        ThanksPageGui.bld_page(self)

    def on_login(self):
        self.transition_exit()
        self.widgets = []
        self.notify('on_push_page', 'login', [self.props])


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
