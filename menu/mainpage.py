from datetime import datetime
import argparse
from feedparser import parse
# from keyring_jeepney import Keyring
from panda3d.core import TextNode
from xml.parsers.expat import ExpatError
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, gaierror, error, \
    SOL_SOCKET, SO_REUSEADDR, timeout
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.mainpage import MainPage, MainPageGui
from yyagl.engine.gui.page import Page, PageFacade, PageGui
from yyagl.engine.logic import VersionChecker
from yyagl.gameobject import GameObject
from yyagl.lib.gui import Btn, Label, Text, Img, Frame
from .optionpage import OptionPageProps


class YorgMainPageGui(MainPageGui):

    def __init__(self, mediator, mainpage_props, yorg_client):
        self.__feed_type = ''
        self.__date_field = ''
        self.props = mainpage_props
        self.yorg_client = yorg_client
        self.load_settings()
        self.conn_attempted = False
        self.ver_check = VersionChecker()
        MainPageGui.__init__(self, mediator, self.props.gameprops.menu_args)
        if self.ver_check.is_uptodate():
            options = self.props.opt_file
            user = options['settings']['login']['usr']
            password = options['settings']['login']['pwd']
            parser = argparse.ArgumentParser()
            parser.add_argument('--user')
            parser.add_argument('--pwd')
            parser.add_argument('--win_orig')
            parser.add_argument('--optfile')
            args = parser.parse_args()
            if args.user and args.pwd:
                user = args.user
                password = args.pwd
            if user and password and yorg_client.is_server_up:
            # if user:
                # if platform.startswith('linux'): set_keyring(Keyring())
                # pwd = get_password('ya2_rog', user)
                # if not pwd:
                    pwd = password
                    # set_password('ya2_rog', user, pwd)
                # self.eng.xmpp.start(user, pwd)
                    #self.eng.xmpp.start(user, pwd, self.on_ok, self.on_ko, self.props.gameprops.xmpp_debug)
                    self.eng.client.register_rpc('login')
                    if not self.eng.client.netw_thr or \
                            not self.eng.client.netw_thr.is_running:
                        yorg_client.restart()
                    while not self.eng.client.netw_thr: pass
                    # wait for the thread
                    ret_val = 'ok'
                    if not yorg_client.authenticated:
                        ret_val = self.eng.client.login(user, password)
                    if ret_val in ['invalid_nick', 'unregistered_nick', 'wrong_pwd']:
                        return self.on_ko(ret_val)
                    taskMgr.doMethodLater(.1, lambda task: self.on_ok(), 'x')
                    # otherwise the menu is not attached to the page yet

            if not (user and password):
                self.on_ko()

    def show(self):
        MainPageGui.show(self)
        self.widgets[2]['text'] = self.get_label()

    def on_ok(self):
        self.yorg_client.authenticated = True
        self.conn_attempted = True
        #self.eng.xmpp.send_connected()
        self.yorg_client.start(self.props.opt_file['settings']['login']['usr'])
        self.notify('on_login')
        self.widgets[2]['text'] = self.get_label()

    def on_ko(self, msg=None):  # unused msg
        self.conn_attempted = True
        self.widgets[2]['text'] = self.get_label()

    def on_logout(self):
        #self.eng.xmpp.disconnect()
        self.yorg_client.authenticated = False
        options = self.props.opt_file
        options['settings']['login']['usr'] = ''
        options['settings']['login']['pwd'] = ''
        options.store()
        self.widgets[2]['text'] = self.get_label()
        self.notify('on_logout')

    def on_login(self):
        self.notify('on_push_page', 'login', [self.props, self.yorg_client])

    def on_loginout(self):
        if self.eng.client.is_active and self.yorg_client.authenticated:
            self.on_logout()
        elif self.conn_attempted:
            self.on_login()

    def load_settings(self):
        sett = self.props.opt_file['settings']
        self.joysticks = sett['joystick1'], sett['joystick2'], sett['joystick3'], sett['joystick4']
        self.keys = sett['keys']
        self.lang = sett['lang']
        self.volume = sett['volume']
        self.fullscreen = sett['fullscreen']
        self.antialiasing = sett['antialiasing']
        self.cars_num = sett['cars_number']
        self.shaders = sett['shaders']
        self.camera = sett['camera']

    def get_label(self):
        if not self.yorg_client.is_server_up:
            return _('Server problem')
        if not self.ver_check.is_uptodate():
            return _('Not up-to-date')
        if self.eng.client.is_active and self.yorg_client.authenticated:
            return _('Log out') + \
                ' \1small\1(%s)\2' % self.props.opt_file['settings']['login']['usr']
        elif self.conn_attempted:
            return _('Log in') + ' \1small\1(' + _('multiplayer') + ')\2'
        #i18n: This is a caption of a button.
        return _('Connecting')

    def build(self):
        sp_cb = lambda: self.notify('on_push_page', 'singleplayer',
                                    [self.props])
        lmp_cb = lambda: self.notify('on_push_page', 'localmp',
                                     [self.props])
        supp_cb = lambda: self.eng.open_browser(self.props.support_url)
        cred_cb = lambda: self.notify('on_push_page', 'credits')
        menu_data = [
            ('Single Player', _('Single Player'), sp_cb),
            ('Server problem', self.get_label(), self.on_loginout),
            ('Local multiplayer', _('Local multiplayer'), lmp_cb),
            ('Options', _('Options'), self.on_options),
            ('Support us', _('Support us'), supp_cb),
            ('Credits', _('Credits'), cred_cb),
            ('Quit', _('Quit'), lambda: self.notify('on_exit'))]
        widgets = [
            Btn(text='', pos=(0, 1, .68-i*.23), command=menu[2],
                tra_src=menu_data[i][0], tra_tra=menu_data[i][1],
                **self.props.gameprops.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        logo_img = Img(
            self.props.title_img, scale=(.64, 1, .64 * (380.0 / 772)),
            parent=base.a2dTopLeft, pos=(.65, 1, -.32))
        widgets += [logo_img]
        lab_args = self.props.gameprops.menu_args.label_args
        lab_args['scale'] = .12
        lab_args['text_fg'] = self.props.gameprops.menu_args.text_err
        wip_lab = Label(
            text='', pos=(.05, 1, -.76), parent=base.a2dTopLeft,
            text_wordwrap=10, text_align=TextNode.A_left,
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
            self.joysticks, self.keys, self.lang, self.volume, self.fullscreen,
            self.antialiasing, self.shaders, self.cars_num, self.camera,
            self.props.opt_file)
        self.notify('on_push_page', 'options', [option_props])

    def set_news(self):
        menu_args = self.props.gameprops.menu_args
        feeds = parse(self.props.feed_url)
        if not feeds['entries']: return
        self.__feed_type = \
            'rss' if 'published' in feeds['entries'][0] else 'atom'
        self.__date_field = \
            'published' if self.__feed_type == 'rss' else 'updated'
        publ = lambda entry: self.__conv(entry[self.__date_field])
        rss = sorted(feeds['entries'], key=publ)
        conv_time = lambda ent: datetime.strftime(self.__conv(ent), '%b %d')
        rss = [(conv_time(ent[self.__date_field]), ent['title'])
               for ent in rss]
        rss.reverse()
        rss = rss[:5]
        rss = [(_rss[0], self.__ellipsis_str(_rss[1])) for _rss in rss]
        frm = Frame(
            frameSize=(0, 1.0, 0, .75), frameColor=(.2, .2, .2, .5),
            pos=(.05, 1, .1), parent=base.a2dBottomLeft)
        texts = [Text(
            _('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32,
            parent='bottomleft', fg=menu_args.text_normal,
            font=menu_args.font, tra_src='Last news:',
            tra_tra=_('Last news:'))]
        rss = [map(self.__to_unicode, rss_str) for rss_str in rss]
        texts += [Text(
            ': '.join(rss[i]), pos=(.1, .65 - i*.1), scale=.055,
            wordwrap=32, parent='bottomleft', align='left',
            fg=menu_args.text_normal, font=menu_args.font)
                  for i in range(min(5, len(rss)))]
        btn_args = self.props.gameprops.menu_args.btn_args.copy()
        btn_args['scale'] = .055
        show_btn = Btn(
            text=_('show'), pos=(.55, 1, .15), command=self.eng.open_browser,
            extraArgs=[self.props.site_url], parent=base.a2dBottomLeft,
            tra_src='show', tra_tra=_('show'), **btn_args)
        self.add_widgets([frm] + texts + [show_btn])

    def __conv(self, datestr):
        if self.__feed_type == 'rss':
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                      'Sep', 'Oct', 'Nov', 'Dec']
            date_el = datestr.split()[1:-2]
            month = months.index(date_el[1]) + 1
            day, year = date_el[0], date_el[2]
            return datetime(int(year), month, int(day))
        else:
            year = int(datestr[:4])
            month = int(datestr[5:7])
            day = int(datestr[8:10])
            return datetime(year, month, day)

    @staticmethod
    def __ellipsis_str(_str):
        return _str if len(_str) <= 20 else _str[:20] + '...'

    @staticmethod
    def __to_unicode(_str):  # for managing different encodings
        try:
            return unicode(_str)
        except UnicodeDecodeError:
            return ''

    def destroy(self):
        self.ver_check.destroy()
        MainPageGui.destroy(self)


class YorgMainPage(MainPage, PageFacade):
    gui_cls = YorgMainPageGui

    def __init__(self, mainpage_props, yorg_client):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, mainpage_props, yorg_client])]]
        GameObject.__init__(self, init_lst)
        # don't construct it using GameObject
        PageFacade.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
