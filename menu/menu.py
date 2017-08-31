from yyagl.gameobject import GameObject, Gui
from yyagl.engine.gui.menu import Menu, MenuLogic, MenuGui
from .mainpage import YorgMainPage, MainPageProps
from .singleplayerpage import SingleplayerPage
from .trackpage import TrackPage
from .carpage import CarPage
from .carpage import CarPageSeason
from .driverpage import DriverPage
from .optionpage import OptionPage
from .inputpage import InputPage
from .creditpage import CreditPage
from .supporterspage import SupportersPage


class MenuProps(object):

    def __init__(
            self, menu_args, opt_file, cars, car_path, phys_path, tracks,
            tracks_tr, track_img, player_name, drivers_img, cars_img,
            multiplayer, title_img, feed_url, site_url, has_save,
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
        self.season_tracks = season_tracks
        self.support_url = support_url
        self.drivers = drivers


class YorgMenuLogic(MenuLogic):

    def on_push_page(self, page_code, args=[]):
        if page_code == 'singleplayer':
            page = SingleplayerPage(self.mdt.gui.menu_args, args[0], self.mdt)
        if page_code == 'single_race':
            page = TrackPage(self.mdt.gui.menu_args, args[0], self.mdt)
        if page_code == 'new_season':
            page = CarPageSeason(self.mdt.gui.menu_args, args[0], self.mdt)
        if page_code == 'car_page':
            page = CarPage(self.mdt.gui.menu_args, args[0], self.mdt)
        if page_code == 'driver_page':
            page = DriverPage(self.mdt.gui.menu_args, args[0], args[1],
                              args[2], self.mdt)
        if page_code == 'options':
            page = OptionPage(self.mdt.gui.menu_args, args[0], self.mdt)
        if page_code == 'input':
            page = InputPage(
                self.mdt.gui.menu_args, args[0], args[1], self.mdt)
        if page_code == 'credits':
            page = CreditPage(self.mdt.gui.menu_args, self.mdt)
        if page_code == 'supporters':
            page = SupportersPage(self.mdt.gui.menu_args, self.mdt)
        self.push_page(page)


class YorgMenuGui(MenuGui):

    def __init__(self, mdt, menu_props):
        # every page should not manage following pages by forwarding params:
        # each page should callback the menu and it should spawn the next one
        MenuGui.__init__(self, mdt, menu_props.menu_args)
        m_p = menu_props
        mainpage_props = MainPageProps(
            m_p.opt_file, m_p.cars, m_p.car_path, m_p.phys_path, m_p.tracks,
            m_p.tracks_tr, m_p.track_img, m_p.player_name, m_p.drivers_img,
            m_p.cars_img, m_p.multiplayer, m_p.title_img, m_p.feed_url,
            m_p.site_url, m_p.has_save, m_p.season_tracks, m_p.support_url,
            m_p.drivers)
        eng.do_later(.01, lambda: self.mdt.logic.push_page(YorgMainPage(self.mdt, mainpage_props)))


class YorgMenu(Menu):
    gui_cls = YorgMenuGui
    logic_cls = YorgMenuLogic
