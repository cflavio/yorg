from random import shuffle
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageGui
from yyagl.engine.gui.imgbtn import ImageButton
from yyagl.gameobject import GameObjectMdt
from .carpage import CarPage, CarPageServer
from .netmsgs import NetMsgs


class TrackPageGui(PageGui):

    def __init__(self, mdt, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the track'), pos=(0, .8),
                           **menu_gui.text_args)
        widgets = [txt]

        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:2]
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        for i in range(len(self.tracks)):
            img = ImageButton(
                scale=.5, pos=(-.5 + i * 1.0, 1, .1), frameColor=(0, 0, 0, 0),
                image=self.track_img % self.tracks[i],
                command=self.on_track, extraArgs=[self.tracks[i]],
                **self.menu.gui.imgbtn_args)
            txt = OnscreenText(self.tracks_tr[i], pos=(-.5 + i * 1.0, .45),
                               scale=.08, **t_a)
            thanks = OnscreenText(_('thanks to:'), pos=(-.5 + i * 1.0, -.2),
                                  scale=.06, **t_a)
            name = OnscreenText(names[i], pos=(-.5 + i * 1.0, -.3), scale=.08,
                                **t_a)
            widgets += [img, txt, thanks, name]
        map(self.add_widget, widgets)
        PageGui.build_page(self)

    def on_track(self, track):
        self.menu.track = track
        self.menu.logic.push_page(CarPage(self.menu, self.cars, self.car_path,
                                          self.phys_path))

    def destroy(self):
        if hasattr(self.menu, 'track'):
            del self.menu.track
        PageGui.destroy(self)


class TrackPageGuiServer(TrackPageGui):

    def on_track(self, track):
        self.menu.track = track
        self.menu.logic.push_page(CarPageServer(self.menu))
        eng.server.send([NetMsgs.track_selected, track])


class TrackPage(Page):
    gui_cls = TrackPageGui

    def __init__(self, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, cars, car_path,
                                    phys_path, tracks, tracks_tr, track_img])]]
        GameObjectMdt.__init__(self, init_lst)


class TrackPageServer(Page):
    gui_cls = TrackPageGuiServer
