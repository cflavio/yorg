from datetime import datetime
from feedparser import parse
from panda3d.core import TextNode
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.engine.gui.mainpage import MainPage, MainPageGui
from yyagl.engine.gui.page import PageGui
from yyagl.gameobject import GameObject
from .singleplayerpage import SingleplayerPage, SingleplayerPageProps
from .multiplayerpage import MultiplayerPage, MultiplayerPageProps
from .optionpage import OptionPage, OptionPageProps
from .creditpage import CreditPage


class MainPageProps(object):

    def __init__(
            self, opt_file, cars, car_path, phys_path, tracks, tracks_tr,
            track_img, player_name, drivers_img, cars_img, multiplayer,
            title_img, feed_url, site_url, has_save, season, season_tracks,
            support_url, drivers):
        self.opt_file = opt_file
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.multiplayer = multiplayer
        self.title_img = title_img
        self.feed_url = feed_url
        self.site_url = site_url
        self.has_save = has_save
        self.season = season
        self.season_tracks = season_tracks
        self.support_url = support_url
        self.drivers = drivers


class YorgMainPageGui(MainPageGui):

    def __init__(self, mdt, menu, mainpage_props):
        self.menu = menu
        self.props = mainpage_props
        self.load_settings()
        MainPageGui.__init__(self, mdt, menu)

    def load_settings(self):
        sett = self.props.opt_file['settings']
        self.joystick = sett['joystick']
        self.keys = sett['keys']
        self.lang = sett['lang']
        self.volume = sett['volume']
        self.fullscreen = sett['fullscreen']
        self.aa = sett['aa']

    def bld_page(self):
        mp_props = MultiplayerPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        sp_props = SingleplayerPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.has_save, self.props.season,
            self.props.season_tracks, self.props.drivers)
        sp_cb = lambda: self.menu.push_page(SingleplayerPage(
            self.menu.gui.menu_args, sp_props, self.menu))
        mp_cb = lambda: self.menu.push_page(MultiplayerPage(
            self.menu.gui.menu_args, mp_props, self.menu))
        supp_cb = lambda: eng.open_browser(self.props.support_url)
        cred_cb = lambda: self.menu.push_page(CreditPage(
            self.menu.gui.menu_args, self.menu))
        menu_data = [
            ('Single Player', _('Single Player'), sp_cb),
            ('Multiplayer', _('Multiplayer'), mp_cb),
            ('Options', _('Options'), self.on_options),
            ('Support us', _('Support us'), supp_cb),
            ('Credits', _('Credits'), cred_cb),
            ('Quit', _('Quit'), lambda: self.mdt.menu.gui.notify('on_exit'))]
        menu_gui = self.menu.gui
        widgets = [
            DirectButton(text='', pos=(0, 1, .45-i*.23), command=menu[2],
                         **menu_gui.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(widgets):
            PageGui.transl_text(wdg, menu_data[i][0], menu_data[i][1])
        if not self.props.multiplayer:
            widgets[-5]['state'] = DISABLED
            _fg = menu_gui.menu_args.btn_args['text_fg']
            _fc = widgets[-5]['frameColor']
            clc = lambda val: max(0, val)
            fgc = (_fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
            widgets[-5]['text_fg'] = fgc
            fcc = (clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3),
                   _fc[3])
            widgets[-5]['frameColor'] = fcc
        widgets += [OnscreenImage(
            self.props.title_img, scale=(.8, 1, .8 * (380.0 / 772)),
            parent=base.a2dTopRight, pos=(-.8, 1, -.4))]
        widgets[-1].setTransparency(True)
        map(self.add_widget, widgets)
        self.set_news()
        MainPageGui.bld_page(self)

    def on_options(self):
        self.load_settings()
        option_props = OptionPageProps(
            self.joystick, self.keys, self.lang, self.volume, self.fullscreen,
            self.aa, self.props.opt_file)
        self.menu.push_page(OptionPage(self.menu.gui.menu_args, option_props,
                                       self.menu))

    def set_news(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        feeds = parse(self.props.feed_url)
        if not feeds['entries']:
            return

        def conv(datestr):
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                      'Sep', 'Oct', 'Nov', 'Dec']
            date_el = datestr.split()[1:-2]
            month = months.index(date_el[1]) + 1
            day, year = date_el[0], date_el[2]
            return datetime(int(year), month, int(day))
        publ = lambda entry: conv(entry['published'])
        rss = sorted(feeds['entries'], key=publ)
        conv_time = lambda ent: datetime.strftime(conv(ent), '%b %d')
        rss = [(conv_time(ent['published']), ent['title']) for ent in rss]
        rss.reverse()
        rss = rss[:5]

        def conv_str(_str):
            return _str if len(_str) <= 20 else _str[:20] + '...'
        rss = [(_rss[0], conv_str(_rss[1])) for _rss in rss]
        frm = DirectFrame(
            frameSize=(0, 1.0, 0, .75), frameColor=(.2, .2, .2, .5),
            pos=(.05, 1, .1), parent=base.a2dBottomLeft)
        texts = [OnscreenText(
            _('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32,
            parent=base.a2dBottomLeft, fg=menu_args.text_bg,
            font=menu_args.font)]
        self.transl_text(texts[-1], 'Last news:', _('Last news:'))

        def to_unicode(_str):  # for managing different encodings
            try:
                return unicode(_str)
            except UnicodeDecodeError:
                return ''
        rss = [map(to_unicode, rss_str) for rss_str in rss]
        texts += [OnscreenText(
            ': '.join(rss[i]), pos=(.1, .65 - i*.1), scale=.055,
            wordwrap=32, parent=base.a2dBottomLeft, align=TextNode.A_left,
            fg=menu_args.text_bg, font=menu_args.font)
                  for i in range(5)]
        btn_args = menu_gui.menu_args.btn_args.copy()
        btn_args['scale'] = .055
        btn = DirectButton(
            text=_('show'), pos=(.55, 1, .15), command=eng.open_browser,
            extraArgs=[self.props.site_url], parent=base.a2dBottomLeft,
            **btn_args)
        self.transl_text(btn, 'show', _('show'))
        map(self.add_widget, [frm] + texts + [btn])


class YorgMainPage(MainPage):
    gui_cls = YorgMainPageGui

    def __init__(self, menu, mainpage_props):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, mainpage_props])]]
        GameObject.__init__(self, init_lst)
