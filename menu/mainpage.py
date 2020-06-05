# from datetime import datetime
import argparse
from urllib.request import urlopen
from urllib.error import URLError
from locale import setlocale, LC_ALL
from xml.etree import ElementTree as etree
from xml.etree.ElementTree import ParseError
from datetime import datetime
# from keyring_jeepney import Keyring
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import DISABLED
from yyagl.engine.gui.mainpage import MainPage, MainPageGui
from yyagl.engine.gui.page import PageFacade
from yyagl.engine.logic import VersionChecker, EngineLogic
from yyagl.lib.gui import Btn, Label, Text, Img, Frame
from .optionpage import OptionPageProps


class YorgMainPageGui(MainPageGui):

    def __init__(self, mediator, mainpage_props, players=[0]):
        self.__feed_type = ''
        self.__date_field = ''
        self.props = mainpage_props
        self.load_settings()
        self.conn_attempted = False
        if not self.eng.client.netw_thr or \
                not self.eng.client.netw_thr.is_running:
            self.eng.client.restart()
        self.ver_check = VersionChecker()
        MainPageGui.__init__(self, mediator, self.props.gameprops.menu_props)
        if self.ver_check.is_uptodate():
            options = self.props.opt_file
            user = options['settings']['login']['usr']
            password = options['settings']['login']['pwd']
            parser = argparse.ArgumentParser()
            parser.add_argument('--user')
            parser.add_argument('--pwd')
            parser.add_argument('--win_orig')
            parser.add_argument('--optfile')
            args = parser.parse_args(EngineLogic.cmd_line())
            if args.user and args.pwd:
                user = args.user
                password = args.pwd
            if user and password and self.eng.client.is_server_up:
                # if user:
                # if platform.startswith('linux'): set_keyring(Keyring())
                # pwd = get_password('ya2_rog', user)
                # if not pwd:
                #     pwd = password
                #     set_password('ya2_rog', user, pwd)
                # self.eng.xmpp.start(user, pwd)
                # self.eng.xmpp.start(user, pwd, self.on_ok, self.on_ko,
                #                     self.props.gameprops.xmpp_debug)
                self.eng.client.register_rpc('login')
                while not self.eng.client.netw_thr: pass
                # wait for the thread
                ret_val = 'ok'
                if not self.eng.client.authenticated:
                    ret_val = self.eng.client.login(user, password)
                if ret_val in ['invalid_nick', 'unregistered_nick',
                               'wrong_pwd']:
                    self.on_ko(ret_val)
                    # return self.on_ko(ret_val)
                taskMgr.doMethodLater(.1, lambda task: self.on_ok(), 'x')
                # otherwise the menu is not attached to the page yet

            if not (user and password):
                self.on_ko()

    def on_ok(self):
        self.eng.client.authenticated = True
        self.conn_attempted = True
        # self.eng.xmpp.send_connected()
        self.eng.client.init(self.props.opt_file['settings']['login']['usr'])
        self.notify('on_login')

    def on_ko(self, msg=None):  # unused msg
        self.conn_attempted = True

    def load_settings(self):
        sett = self.props.opt_file['settings']
        self.keys = sett['keys']
        self.lang = sett['lang']
        self.volume = sett['volume']
        self.fullscreen = sett['fullscreen']
        self.antialiasing = sett['antialiasing']
        self.cars_num = sett['cars_number']
        self.shaders = sett['shaders']
        self.camera = sett['camera']

    def build(self):  # parameters differ from overridden
        sp_cb = lambda: self.notify('on_push_page', 'singleplayer',
                                    [self.props])
        mp_cb = lambda: self.notify('on_push_page', 'multiplayer',
                                    [self.props])
        supp_cb = lambda: self.eng.open_browser(self.props.support_url)
        cred_cb = lambda: self.notify('on_push_page', 'credits')
        menu_data = [
            ('Single Player', _('Single Player'), sp_cb),
            ('Multiplayer', _('Multiplayer'), mp_cb),
            ('Options', _('Options'), self.on_options),
            ('Support us', _('Support us'), supp_cb),
            ('Credits', _('Credits'), cred_cb),
            ('Quit', _('Quit'), lambda: self.notify('on_exit'))]
        widgets = [
            Btn(text='', pos=(0, .64-i*.23), cmd=menu[2],
                tra_src=menu_data[i][0], tra_tra=menu_data[i][1],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        logo_img = Img(
            self.props.title_img, scale=(.64, 1, .64 * (380.0 / 772)),
            parent=base.a2dTopLeft, pos=(.65, -.32))
        widgets += [logo_img]
        lab_args = self.props.gameprops.menu_props.label_args
        lab_args['scale'] = .12
        lab_args['text_fg'] = self.props.gameprops.menu_props.text_err_col
        wip_lab = Label(
            text='', pos=(-.05, -1.58), parent=base.a2dTopRight,
            text_wordwrap=10, text_align=TextNode.A_right,
            tra_src='Note: the game is work-in-progress',
            tra_tra=_('Note: the game is work-in-progress'),
            **lab_args)
        self.widgets += [wip_lab]
        self.add_widgets(widgets)
        self.set_news()
        MainPageGui.build(self)
        if not self.ver_check.is_uptodate():
            self.widgets[2]['state'] = DISABLED

    def on_options(self):
        self.load_settings()
        option_props = OptionPageProps(
            self.keys, self.lang, self.volume, self.fullscreen,
            self.antialiasing, self.shaders, self.cars_num, self.camera,
            self.props.opt_file)
        self.notify('on_push_page', 'options', [option_props])

    def set_news(self):
        menu_props = self.props.gameprops.menu_props
        try: feed = urlopen(self.props.feed_url).read()
        except URLError: feed = ''
        try: items = etree.fromstring(feed).findall('channel/item')
        except ParseError: items = []  # e.g. when it is offline
        setlocale(LC_ALL, 'en_US.UTF-8')
        try:
            entries = [(datetime.strptime(
                        entry.findtext('pubDate')[:25],
                        '%a, %d %b %Y %H:%M:%S'),
                        entry.findtext('title') or '')
                       for entry in items]
        except (TypeError, ValueError): entries = []
        entries = list(reversed(sorted(entries,
                                       key=lambda entry: entry[0])))[:5]
        entries = [(datetime.strftime(entry[0], '%b %d'),
                    self.__ellipsis_str(entry[1])) for entry in entries]
        frm = Frame(
            frame_size=(0, 1.0, 0, .75), frame_col=(.2, .2, .2, .5),
            pos=(.05, .1), parent=base.a2dBottomLeft)
        texts = [Text(
            _('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32,
            parent='bottomleft', fg=menu_props.text_normal_col,
            font=menu_props.font, tra_src='Last news:',
            tra_tra=_('Last news:'))]
        texts += [Text(
            ': '.join(entries[i]), pos=(.1, .65 - i*.1), scale=.055,
            wordwrap=32, parent='bottomleft', align='left',
            fg=menu_props.text_normal_col, font=menu_props.font)
                  for i in range(min(5, len(entries)))]
        btn_args = self.props.gameprops.menu_props.btn_args.copy()
        btn_args['scale'] = (.055, .055)
        show_btn = Btn(
            text=_('show'), pos=(.55, .15), cmd=self.eng.open_browser,
            extra_args=[self.props.site_url], parent=base.a2dBottomLeft,
            tra_src='show', tra_tra=_('show'), **btn_args)
        self.add_widgets([frm] + texts + [show_btn])

    @staticmethod
    def __ellipsis_str(_str):
        return _str if len(_str) <= 20 else _str[:20] + '...'

    def destroy(self):
        self.ver_check.destroy()
        MainPageGui.destroy(self)


class YorgMainPage(MainPage, PageFacade):
    gui_cls = YorgMainPageGui

    def __init__(self, mainpage_props):
        self.mainpage_props = mainpage_props
        MainPage.__init__(self, mainpage_props)

    @property
    def init_lst(self):
        return [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.mainpage_props])]]

    def destroy(self):
        MainPage.destroy(self)
