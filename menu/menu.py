from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import Menu
from .mainpage import YorgMainPage


class MenuProps(object):

    def __init__(
            self, menu_args, opt_file, cars, car_path, phys_path, tracks,
            tracks_tr, track_img, player_name, drivers_img, cars_img,
            multiplayer, title_img, feed_url, site_url, has_save, season,
            season_tracks, support_url, drivers):
        self.menu_args = menu_args
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


class YorgMenuGui(Gui):

    def __init__(
            self, mdt, menu_args, opt_file, cars, car_path, phys_path, tracks,
            tracks_tr, track_img, player_name, drivers_img, cars_img,
            multiplayer, title_img, feed_url, site_url, has_save, season,
            season_tracks, support_url, drivers):
        Gui.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(YorgMainPage(
            self.menu, opt_file, cars, car_path, phys_path, tracks, tracks_tr,
            track_img, player_name, drivers_img, cars_img,
            multiplayer, title_img, feed_url, site_url, has_save, season,
            season_tracks, support_url, drivers))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class YorgMenu(GameObjectMdt):

    def __init__(self, menu_props):
        m_p = menu_props
        init_lst = [[('gui', YorgMenuGui, [
            self, m_p.menu_args, m_p.opt_file, m_p.cars, m_p.car_path,
            m_p.phys_path, m_p.tracks, m_p.tracks_tr, m_p.track_img,
            m_p.player_name, m_p.drivers_img, m_p.cars_img, m_p.multiplayer,
            m_p.title_img, m_p.feed_url, m_p.site_url, m_p.has_save,
            m_p.season, m_p.season_tracks, m_p.support_url, m_p.drivers])]]
        GameObjectMdt.__init__(self, init_lst)
