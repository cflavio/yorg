from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yyagl.engine.gui.imgbtn import ImageButton
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

    def build_page(self):
        menu_gui = self.menu.gui
        widgets = [OnscreenText(text=_('Select the track'), pos=(0, .8),
                                **menu_gui.text_args)]
        t_a = self.menu.gui.text_args.copy()
        t_a['scale'] = .08
        for i in range(len(self.props.tracks)):
            widgets += [ImageButton(
                scale=.5, pos=(-.5 + i * 1.0, 1, .1), frameColor=(0, 0, 0, 0),
                image=self.props.track_img % self.props.tracks[i],
                command=self.on_track, extraArgs=[self.props.tracks[i]],
                **self.menu.gui.imgbtn_args)]
            widgets += [OnscreenText(self.props.tracks_tr[i],
                                     pos=(-.5 + i * 1.0, -.32), **t_a)]
        map(self.add_widget, widgets)
        ThanksPageGui.build_page(self)

    def on_track(self, track):
        self.menu.track = track
        carpage_props = CarPageProps(
            self.props.cars, self.props.car_path, self.props.phys_path,
            self.props.player_name, self.props.drivers_img,
            self.props.cars_img, self.props.drivers)
        self.menu.push_page(CarPage(self.menu, carpage_props))

    def destroy(self):
        if hasattr(self.menu, 'track'):
            del self.menu.track
        PageGui.destroy(self)


class TrackPageGuiServer(TrackPageGui):

    def on_track(self, track):
        self.menu.track = track
        self.menu.push_page(CarPageServer(self.menu))
        eng.server_send([NetMsgs.track_selected, track])


class TrackPage(Page):
    gui_cls = TrackPageGui

    def __init__(self, menu, trackpage_props):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, trackpage_props])]]
        GameObject.__init__(self, init_lst)


class TrackPageServer(TrackPage):
    gui_cls = TrackPageGuiServer
