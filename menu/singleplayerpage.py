from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .trackpage import TrackPageProps
from .thankspage import ThanksPageGui


class SingleplayerPageProps(object):

    def __init__(self, cars, car_path, phys_path, tracks, tracks_tr, track_img,
                 player_name, drivers_img, cars_img, has_save, season_tracks,
                 drivers, menu_args):
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
        self.season_tracks = season_tracks
        self.drivers = drivers
        self.menu_args = menu_args


class SingleplayerPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, props):
        self.props = props
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
        menu_data = [
            (_('Single race'), self.on_single_race),
            (_('New season'), self.on_start),
            (_('Continue season'), lambda: self.notify('on_continue'))]
        widgets = [
            DirectButton(
                text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                **self.props.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        map(self.add_widget, widgets)
        self._set_buttons()
        if not self.props.has_save:
            widgets[-1].disable()
        ThanksPageGui.bld_page(self)

    def on_single_race(self):
        trackpage_props = TrackPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.notify('on_push_page', 'single_race', [trackpage_props])

    def on_start(self):
        self.notify('on_track_selected', self.props.season_tracks[0])
        trackpage_props = TrackPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.tracks, self.props.tracks_tr, self.props.track_img,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.notify('on_push_page', 'new_season', [trackpage_props])


class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui

    def __init__(self, menu_args, singleplayerpage_props):
        self.menu_args = menu_args
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args,
                                    singleplayerpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
