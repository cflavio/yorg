from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.engine.network.server import Server
from yyagl.gameobject import GameObject
from .carpage import CarPage, CarPageServer, CarPageProps
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class TrackPageProps(object):

    def __init__(self, cars, car_path, phys_path, tracks, tracks_tr, track_img,
                 player_name, drivers_img, cars_img, drivers):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.drivers = drivers


class TrackPageGui(ThanksPageGui):

    def __init__(self, mdt, menu, trackpage_props):
        self.props = trackpage_props
        ThanksPageGui.__init__(self, mdt, menu)

    def bld_page(self):
        menu_gui = self.mdt.menu.gui
        widgets = [OnscreenText(text=_('Select the track'), pos=(0, .8),
                                **menu_gui.menu_args.text_args)]
        t_a = self.mdt.menu.gui.menu_args.text_args.copy()
        t_a['scale'] = .08
        for i in range(len(self.props.tracks)):
            widgets += [ImgBtn(
                scale=.5, pos=(-1.05 + i * 1.05, 1, .1),
                frameColor=(0, 0, 0, 0),
                image=self.props.track_img % self.props.tracks[i],
                command=self.on_track, extraArgs=[self.props.tracks[i]],
                **self.mdt.menu.gui.menu_args.imgbtn_args)]
            widgets += [OnscreenText(self.props.tracks_tr[i],
                                     pos=(-1.05 + i * 1.05, -.32), **t_a)]
        map(self.add_widget, widgets)
        ThanksPageGui.bld_page(self)

    def on_track(self, track):
        self.mdt.menu.track = track
        carpage_props = CarPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.mdt.menu.push_page(CarPage(
            self.mdt.menu.gui.menu_args, carpage_props, self.mdt.menu))

    def destroy(self):
        if hasattr(self.mdt.menu, 'track'):
            del self.mdt.menu.track
        PageGui.destroy(self)


class TrackPageGuiServer(TrackPageGui):

    def on_track(self, track):
        self.menu.track = track
        self.menu.push_page(CarPageServer(self.menu))
        Server().send([NetMsgs.track_selected, track])


class TrackPage(Page):
    gui_cls = TrackPageGui

    def __init__(self, menu_args, trackpage_props, menu):
        self.menu_args = menu_args
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, trackpage_props])]]
        GameObject.__init__(self, init_lst)


class TrackPageServer(TrackPage):
    gui_cls = TrackPageGuiServer
