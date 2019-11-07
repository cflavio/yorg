from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from yyagl.engine.logic import VersionChecker
from .thankspage import ThanksPageGui


class OnlinePageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        self.ver_check = VersionChecker()
        self.conn_attempted = True
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        lmp_cb = lambda: self.notify('on_push_page', 'localmp',
                                     [self.props])
        menu_data = []
        top = .3
        if self.eng.client.is_active and self.eng.client.authenticated:
            menu_data = [
                ('Play', _('Play'), self.on_play)]
            top = .5
        menu_data += [
            ('Server problem', self.get_label(), self.on_loginout),
            ('Register', _('Register'), self.on_register),
            ('Reset password', _('Reset password'), self.on_reset)]
        widgets = [
            Btn(text=menu[0], pos=(0, top-i*.28), cmd=menu[2],
                tra_src=menu[0], tra_tra=menu[1],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        self.__loginout_btn = widgets[-3]
        self.add_widgets(widgets)
        ThanksPageGui.build(self)

    def on_logout(self):
        #self.eng.xmpp.disconnect()
        self.widgets[5].destroy()
        self.widgets.remove(self.widgets[5])
        self.eng.client.authenticated = False
        options = self.props.opt_file
        options['settings']['login']['usr'] = ''
        options['settings']['login']['pwd'] = ''
        options.store()
        self.__loginout_btn['text'] = self.get_label()
        self.notify('on_logout')

    def on_play(self):
        self.notify('on_push_page', 'onlineplay', [self.props])

    def on_login(self):
        self.notify('on_push_page', 'login', [self.props])

    def on_loginout(self):
        if not self.eng.client.is_server_up: return
        if self.eng.client.is_active and self.eng.client.authenticated:
            self.on_logout()
        elif self.conn_attempted:
            self.on_login()

    def get_label(self):
        if not self.eng.client.is_server_up:
            return _('Server problem')
        if not self.ver_check.is_uptodate():
            return _('Not up-to-date')
        if self.eng.client.is_active and self.eng.client.authenticated:
            return _('Log out') + \
                ' \1small\1(%s)\2' % self.props.opt_file['settings']['login']['usr']
        elif self.conn_attempted:
            return _('Log in') + ' \1small\1(' + _('multiplayer') + ')\2'
        #i18n: This is a caption of a button.
        return _('Connecting')

    def on_register(self):
        self.notify('on_push_page', 'register', [self.props])

    def on_reset(self):
        self.notify('on_push_page', 'reset', [self.props])


class OnlinePage(Page):
    gui_cls = OnlinePageGui

    def __init__(self, mp_props):
        GameObject.__init__(self)
        self.event = self.event_cls(self)
        self.gui = self.gui_cls(self, mp_props)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        self.event.destroy()
        self.gui.destroy()
        GameObject.destroy(self)
        PageFacade.destroy(self)
