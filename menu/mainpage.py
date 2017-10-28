from datetime import datetime
from feedparser import parse
from panda3d.core import TextNode
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.mainpage import MainPage, MainPageGui
from yyagl.engine.gui.page import PageGui
from yyagl.gameobject import GameObject
from .multiplayerpage import MultiplayerPage
from .optionpage import OptionPageProps


class YorgMainPageGui(MainPageGui):

    def __init__(self, mdt, mainpage_props):
        self.props = mainpage_props
        self.load_settings()
        MainPageGui.__init__(self, mdt, self.props.gameprops.menu_args)

    def load_settings(self):
        sett = self.props.opt_file['settings']
        self.joystick = sett['joystick']
        self.keys = sett['keys']
        self.lang = sett['lang']
        self.volume = sett['volume']
        self.fullscreen = sett['fullscreen']
        self.antialiasing = sett['antialiasing']
        self.cars_num = sett['cars_number']
        self.shaders = sett['shaders']

    def bld_page(self):
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
            DirectButton(text='', pos=(0, 1, .45-i*.23), command=menu[2],
                         **self.props.gameprops.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(widgets):
            PageGui.transl_text(wdg, menu_data[i][0], menu_data[i][1])
        logo_img = OnscreenImage(
            self.props.title_img, scale=(.8, 1, .8 * (380.0 / 772)),
            parent=base.a2dTopRight, pos=(-.8, 1, -.4))
        widgets += [logo_img]
        widgets[-1].set_transparency(True)
        lab_args = self.props.gameprops.menu_args.label_args
        lab_args['scale'] = .12
        lab_args['text_fg'] = self.props.gameprops.menu_args.text_err
        wip_lab = DirectLabel(
            text='', pos=(.05, 1, -.15), parent=base.a2dTopLeft,
            text_align=TextNode.A_left, **lab_args)
        PageGui.transl_text(wip_lab, 'Note: the game is work-in-progress',
                            _('Note: the game is work-in-progress'))
        self.widgets += [wip_lab]
        map(self.add_widget, widgets)
        self.set_news()
        MainPageGui.bld_page(self)

    def on_options(self):
        self.load_settings()
        option_props = OptionPageProps(
            self.joystick, self.keys, self.lang, self.volume, self.fullscreen,
            self.antialiasing, self.shaders, self.cars_num,
            self.props.opt_file)
        self.notify('on_push_page', 'options', [option_props])

    def set_news(self):
        menu_args = self.props.gameprops.menu_args
        feeds = parse(self.props.feed_url)
        if not feeds['entries']: return
        self.__feed_type = 'rss' if 'published' in feeds['entries'][0] else 'atom'
        self.__date_field = 'published' if self.__feed_type == 'rss' else 'updated'
        publ = lambda entry: self.__conv(entry[self.__date_field])
        rss = sorted(feeds['entries'], key=publ)
        conv_time = lambda ent: datetime.strftime(self.__conv(ent), '%b %d')
        rss = [(conv_time(ent[self.__date_field]), ent['title']) for ent in rss]
        rss.reverse()
        rss = rss[:5]
        rss = [(_rss[0], self.__ellipsis_str(_rss[1])) for _rss in rss]
        frm = DirectFrame(
            frameSize=(0, 1.0, 0, .75), frameColor=(.2, .2, .2, .5),
            pos=(.05, 1, .1), parent=base.a2dBottomLeft)
        texts = [OnscreenText(
            _('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32,
            parent=base.a2dBottomLeft, fg=menu_args.text_bg,
            font=menu_args.font)]
        self.transl_text(texts[-1], 'Last news:', _('Last news:'))
        rss = [map(self.__to_unicode, rss_str) for rss_str in rss]
        texts += [OnscreenText(
            ': '.join(rss[i]), pos=(.1, .65 - i*.1), scale=.055,
            wordwrap=32, parent=base.a2dBottomLeft, align=TextNode.A_left,
            fg=menu_args.text_bg, font=menu_args.font)
                  for i in range(min(5, len(rss)))]
        btn_args = self.props.gameprops.menu_args.btn_args.copy()
        btn_args['scale'] = .055
        show_btn = DirectButton(
            text=_('show'), pos=(.55, 1, .15), command=self.eng.open_browser,
            extraArgs=[self.props.site_url], parent=base.a2dBottomLeft,
            **btn_args)
        self.transl_text(show_btn, 'show', _('show'))
        map(self.add_widget, [frm] + texts + [show_btn])

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


class YorgMainPage(MainPage):
    gui_cls = YorgMainPageGui

    def __init__(self, mainpage_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, mainpage_props])]]
        GameObject.__init__(self, init_lst)
        # don't construct it using GameObject
        MainPage.__init__(self)

    def destroy(self):
        GameObject.destroy(self)
        MainPage.destroy(self)
