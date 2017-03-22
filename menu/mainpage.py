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
from yyagl.gameobject import GameObjectMdt
from .singleplayerpage import SingleplayerPage
from .multiplayerpage import MultiplayerPage
from .optionpage import OptionPage
from .creditpage import CreditPage


class YorgMainPageGui(MainPageGui):

    def __init__(self, mdt, menu, opt_file, cars, car_path, phys_path, tracks,
                 tracks_tr, track_img, player_name, drivers_img, cars_img,
                 multiplayer, title_img, feed_url, site_url, has_save, season,
                 season_tracks):
        self.menu = menu
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
        self.opt_file = opt_file
        self.load_settings()
        MainPageGui.__init__(self, mdt, menu)

    def load_settings(self):
        sett = self.opt_file['settings']
        self.joystick = sett['joystick']
        self.keys = sett['keys']
        self.lang = sett['lang']
        self.volume = sett['volume']
        self.fullscreen = sett['fullscreen']
        self.aa = sett['aa']

    def build_page(self):
        menu_data = [
            ('Single Player', _('Single Player'),
             lambda: self.menu.push_page(SingleplayerPage(
                 self.menu, self.cars, self.car_path, self.phys_path,
                 self.tracks, self.tracks_tr, self.track_img, self.player_name,
                 self.drivers_img, self.cars_img, self.has_save, self.season,
                 self.season_tracks))),
            ('Multiplayer', _('Multiplayer'),
             lambda: self.menu.push_page(MultiplayerPage(
                 self.menu, self.cars, self.car_path, self.phys_path,
                 self.tracks, self.tracks_tr, self.track_img, self.player_name,
                 self.drivers_img, self.cars_img))),
            ('Options', _('Options'), self.on_options),
            ('Credits', _('Credits'),
             lambda: self.menu.push_page(CreditPage(self.menu))),
            ('Quit', _('Quit'), lambda: self.mdt.menu.gui.notify('on_exit'))]
        menu_gui = self.menu.gui
        widgets = [
            DirectButton(text='', pos=(0, 1, .4-i*.28), command=menu[2],
                         **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(widgets):
            PageGui.transl_text(wdg, menu_data[i][0], menu_data[i][1])
        if not self.multiplayer:
            widgets[-4]['state'] = DISABLED
            _fg = menu_gui.btn_args['text_fg']
            _fc = widgets[-4]['frameColor']
            clc = lambda val: max(0, val)
            widgets[-4]['text_fg'] = (
                _fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
            widgets[-4]['frameColor'] = (
                clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3), _fc[3])
        widgets += [OnscreenImage(
            self.title_img,
            scale=(.8, 1, .8 * (380.0 / 772)), parent=base.a2dTopRight,
            pos=(-.8, 1, -.4))]
        widgets[-1].setTransparency(True)
        map(self.add_widget, widgets)
        self.set_news()
        MainPageGui.build_page(self)

    def on_options(self):
        self.load_settings()
        self.menu.logic.push_page(OptionPage(
            self.menu, self.joystick, self.keys, self.lang, self.volume,
            self.fullscreen, self.aa))

    def set_news(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        feeds = parse(self.feed_url)
        entries = [feed for feed in feeds['entries']]

        def conv(datestr):
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                      'Sep', 'Oct', 'Nov', 'Dec']
            date_el = datestr.split()[1:-2]
            month = months.index(date_el[1]) + 1
            day, year = date_el[0], date_el[2]
            return datetime(int(year), month, int(day))
        rss = sorted(entries, key=lambda entry: conv(entry['published']))
        rss = [(datetime.strftime(conv(ent['published']), '%b %d'),
                ent['title']) for ent in rss]
        rss.reverse()
        rss = rss[:5]

        def conv_str(_str):
            return _str if len(_str) <= 20 else _str[:20] + '...'
        if not rss:
            return
        rss = [(_rss[0], conv_str(_rss[1])) for _rss in rss]
        frm = DirectFrame(
            frameSize=(0, 1.0, 0, .75), frameColor=(.2, .2, .2, .5),
            pos=(.05, 1, .1), parent=base.a2dBottomLeft)
        texts = []
        txt = OnscreenText(
            _('Last news:'), pos=(.55, .75), scale=.055, wordwrap=32,
            parent=base.a2dBottomLeft, fg=menu_args.text_bg,
            font=menu_args.font)
        texts += [txt]
        for i in range(5):
            txt = OnscreenText(
                ': '.join(rss[i]), pos=(.1, .65 - i*.1), scale=.055,
                wordwrap=32, parent=base.a2dBottomLeft, align=TextNode.A_left,
                fg=menu_args.text_bg, font=menu_args.font)
            texts += [txt]
        btn_args = menu_gui.btn_args.copy()
        btn_args['scale'] = .055
        btn = DirectButton(
            text=_('show'), pos=(.55, 1, .15), command=eng.open_browser,
            extraArgs=[self.site_url], parent=base.a2dBottomLeft,
            **btn_args)
        map(self.add_widget, [frm] + texts + [btn])


class YorgMainPage(MainPage):
    gui_cls = YorgMainPageGui

    def __init__(self, menu, opt_file, cars, car_path, phys_path, tracks,
                 tracks_tr, track_img, player_name, drivers_img, cars_img,
                 multiplayer, title_img, feed_url, site_url, has_save, season,
                 season_tracks):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [
                self, self.menu, opt_file, cars, car_path, phys_path, tracks,
                tracks_tr, track_img, player_name, drivers_img, cars_img,
                multiplayer, title_img, feed_url, site_url, has_save, season,
                season_tracks])]]
        GameObjectMdt.__init__(self, init_lst)
