from collections import namedtuple
from yyagl.gameobject import GameObject, Gui
from yyagl.engine.gui.menu import Menu, MenuLogic, MenuGui
from .mainpage import YorgMainPage
from .singleplayerpage import SingleplayerPage
from .trackpage import TrackPage
from .carpage import CarPage
from .carpage import CarPageSeason
from .driverpage import DriverPage
from .optionpage import OptionPage
from .inputpage import InputPage
from .creditpage import CreditPage
from .supporterspage import SupportersPage


__fields = 'gameprops opt_file multiplayer title_img feed_url site_url ' + \
    'has_save support_url'
MenuProps = namedtuple('MenuProps',  __fields)


class YorgMenuLogic(MenuLogic):

    def on_push_page(self, page_code, args=[]):
        if page_code == 'singleplayer':
            page = SingleplayerPage(self.mdt.gui.menu_args, args[0])
            page.gui.attach(self.on_track_selected)
            page.gui.attach(self.on_continue)
        if page_code == 'single_race':
            page = TrackPage(self.mdt.gui.menu_args, args[0])
            page.gui.attach(self.on_track_selected)
        if page_code == 'new_season':
            page = CarPageSeason(self.mdt.gui.menu_args, args[0], self.mdt.track)
            page.gui.attach(self.on_car_selected_season)
        if page_code == 'car_page':
            page = CarPage(self.mdt.gui.menu_args, args[0], self.mdt.track)
            page.gui.attach(self.on_car_selected)
        if page_code == 'driver_page':
            page = DriverPage(self.mdt.gui.menu_args, args[0], args[1],
                              args[2])
            page.gui.attach(self.on_driver_selected)
        if page_code == 'options':
            page = OptionPage(self.mdt.gui.menu_args, args[0])
        if page_code == 'input':
            page = InputPage(
                self.mdt.gui.menu_args, args[0], args[1])
        if page_code == 'credits':
            page = CreditPage(self.mdt.gui.menu_args)
        if page_code == 'supporters':
            page = SupportersPage(self.mdt.gui.menu_args)
        self.push_page(page)

    def on_back(self, page_code, args=[]):
        if page_code == 'input_page':
            self.mdt.gui.notify('on_input_back', args[0])
        if page_code == 'options_page':
            self.mdt.gui.notify('on_options_back', args[0])
        MenuLogic.on_back(self, page_code, args)

    def on_track_selected(self, track):
        self.mdt.track = track

    def on_car_selected(self, car):
        self.mdt.gui.notify('on_car_selected', car)

    def on_car_selected_season(self, car):
        self.mdt.gui.notify('on_car_selected_season', car)

    def on_driver_selected(self, name, drivers, track, car):
        self.mdt.gui.notify('on_driver_selected', name, drivers, track, car)

    def on_continue(self):
        self.mdt.gui.notify('on_continue')


class YorgMenuGui(MenuGui):

    def __init__(self, mdt, menu_props):
        # every page should not manage following pages by forwarding params:
        # each page should callback the menu and it should spawn the next one
        MenuGui.__init__(self, mdt, menu_props.gameprops.menu_args)
        m_p = menu_props
        page = YorgMainPage(menu_props)
        page.gui.attach(self.on_exit)
        self.eng.do_later(.01, lambda: self.mdt.logic.push_page(page))

    def on_exit(self):
        self.notify('on_exit')


class YorgMenu(Menu):
    gui_cls = YorgMenuGui
    logic_cls = YorgMenuLogic
