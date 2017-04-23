from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED
from yyagl.engine.gui.page import Page
from yyagl.gameobject import GameObject
from .carpage import CarPageSeason
from .trackpage import TrackPage, TrackPageProps
from .thankspage import ThanksPageGui


class SingleplayerPageProps(object):

    def __init__(self, cars, car_path, phys_path, tracks, tracks_tr, track_img,
                 player_name, drivers_img, cars_img, has_save, season,
                 season_tracks, drivers):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.has_save = has_save
        self.season = season
        self.season_tracks = season_tracks
        self.drivers = drivers


class SingleplayerPageGui(ThanksPageGui):

    def __init__(self, mdt, menu, singleplayer_props):
        self.props = singleplayer_props
        ThanksPageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_data = [
            (_('Single race'), self.on_single_race),
            (_('New season'), self.on_start),
            (_('Continue season'), self.on_continue)]
        widgets = [
            DirectButton(
                text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        if not self.props.has_save:
            widgets[-1]['state'] = DISABLED  # do wdg.disable()
            widgets[-1].setAlphaScale(.25)
        if not self.props.season:
            for idx in [-2, -1]:
                widgets[idx]['state'] = DISABLED
                _fg = menu_gui.btn_args['text_fg']
                _fc = widgets[idx]['frameColor']
                clc = lambda val: max(0, val)
                fgc = (_fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
                widgets[idx]['text_fg'] = fgc
                fcc = (clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3),
                       _fc[3])
                widgets[idx]['frameColor'] = fcc
        map(self.add_widget, widgets)
        ThanksPageGui.build_page(self)

    def on_single_race(self):
        trackpage_props = TrackPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.menu.push_page(TrackPage(self.menu, trackpage_props))

    def on_start(self):
        self.menu.track = self.props.season_tracks[0]
        trackpage_props = TrackPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.menu.push_page(CarPageSeason(self.menu, trackpage_props))

    def on_continue(self):
        self.mdt.menu.gui.notify('on_continue')


class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui

    def __init__(self, menu, singleplayerpage_props):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, singleplayerpage_props])]]
        GameObject.__init__(self, init_lst)
