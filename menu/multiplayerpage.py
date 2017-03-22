from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageGui
from yyagl.gameobject import GameObjectMdt
from .serverpage import ServerPage
from .clientpage import ClientPage
from .thankspage import ThanksPageGui


class MultiplayerPageGui(ThanksPageGui):

    def __init__(self, mdt, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img, player_name, drivers_img, cars_img):
        self.cars = cars
        self.car_path = car_path
        self.phys_path = phys_path
        self.tracks = tracks
        self.tracks_tr = tracks_tr
        self.track_img = track_img
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        ThanksPageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_data = [
            ('Server',
             lambda: self.menu.logic.push_page(ServerPage(
                 self.menu, self.cars, self.car_path, self.phys_path,
                 self.tracks, self.tracks_tr, self.track_img, self.player_name,
                 self.drivers_img, self.cars_img))),
            ('Client',
             lambda: self.menu.logic.push_page(ClientPage(self.menu)))]
        widgets = [
            DirectButton(text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                         **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        map(self.add_widget, widgets)
        ThanksPageGui.build_page(self)


class MultiplayerPage(Page):
    gui_cls = MultiplayerPageGui

    def __init__(self, menu, cars, car_path, phys_path, tracks, tracks_tr,
                 track_img, player_name, drivers_img, cars_img):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [
                self, self.menu, cars, car_path, phys_path, tracks, tracks_tr,
                track_img, player_name, drivers_img, cars_img])]]
        GameObjectMdt.__init__(self, init_lst)
