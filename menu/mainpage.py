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
from .singleplayerpage import SingleplayerPageProps
from .multiplayerpage import MultiplayerPage, MultiplayerPageProps
from .optionpage import OptionPageProps


class MainPageProps(object):

    def __init__(
            self, opt_file, cars, car_path, phys_path, tracks, tracks_tr,
            track_img, player_name, drivers_img, cars_img, multiplayer,
            title_img, feed_url, site_url, has_save, season_tracks,
            support_url, drivers, menu_args):
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
        self.season_tracks = season_tracks
        self.support_url = support_url
        self.drivers = drivers
        self.menu_args = menu_args


class YorgMainPageGui(MainPageGui):

    def __init__(self, mdt, mainpage_props):
        self.props = mainpage_props
        self.load_settings()
        MainPageGui.__init__(self, mdt, self.props.menu_args)

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
        mp_props = MultiplayerPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        sp_props = SingleplayerPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.has_save, self.props.season_tracks,
            self.props.drivers, self.props.menu_args)
        sp_cb = lambda: self.notify('on_push_page', 'singleplayer', [sp_props])
        mp_cb = lambda: self.menu.push_page(MultiplayerPage(
            self.menu.gui.menu_args, mp_props, self.menu))
        supp_cb = lambda: eng.open_browser(self.props.support_url)
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
                         **self.props.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(widgets):
            PageGui.transl_text(wdg, menu_data[i][0], menu_data[i][1])
        if not self.props.multiplayer:
            widgets[-5]['state'] = DISABLED
            _fg = self.props.menu_args.btn_args['text_fg']
            _fc = widgets[-5]['frameColor']
            clc = lambda val: max(0, val)
            fgc = (_fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
            widgets[-5]['text_fg'] = fgc
            fcc = (clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3),
                   _fc[3])
            widgets[-5]['frameColor'] = fcc
        logo_img = OnscreenImage(
            self.props.title_img, scale=(.8, 1, .8 * (380.0 / 772)),
            parent=base.a2dTopRight, pos=(-.8, 1, -.4))
        widgets += [logo_img]
        widgets[-1].set_transparency(True)
        lab_args = self.props.menu_args.label_args
        lab_args['scale'] = .12
        lab_args['text_fg'] = self.props.menu_args.text_err
        wip_lab = DirectLabel(text='', pos=(.05, 1, -.15), parent=base.a2dTopLeft,
                             text_align=TextNode.A_left, **lab_args)
        PageGui.transl_text(wip_lab, 'NB the game is work-in-progress',
                            _('NB the game is work-in-progress'))
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
        menu_args = self.props.menu_args
        feeds = parse(self.props.feed_url)
        if not feeds['entries']:
            return
        publ = lambda entry: self.__conv(entry['published'])
        rss = sorted(feeds['entries'], key=publ)
        conv_time = lambda ent: datetime.strftime(self.__conv(ent), '%b %d')
        rss = [(conv_time(ent['published']), ent['title']) for ent in rss]
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
                  for i in range(5)]
        btn_args = self.props.menu_args.btn_args.copy()
        btn_args['scale'] = .055
        show_btn = DirectButton(
            text=_('show'), pos=(.55, 1, .15), command=eng.open_browser,
            extraArgs=[self.props.site_url], parent=base.a2dBottomLeft,
            **btn_args)
        self.transl_text(show_btn, 'show', _('show'))
        map(self.add_widget, [frm] + texts + [show_btn])

    @staticmethod
    def __conv(datestr):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                  'Sep', 'Oct', 'Nov', 'Dec']
        date_el = datestr.split()[1:-2]
        month = months.index(date_el[1]) + 1
        day, year = date_el[0], date_el[2]
        return datetime(int(year), month, int(day))

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
        MainPage.__init__(self)
