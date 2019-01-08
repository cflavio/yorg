from yyagl.engine.gui.menu import Menu, MenuLogic, MenuGui, MenuFacade
from yyagl.gameobject import GameObject
from .mainpage import YorgMainPage
from .singleplayerpage import SingleplayerPage
from .multiplayerpage import MultiplayerPage
from .onlinepage import OnlinePage
from .onlineplaypage import OnlinePlayPage
from .clientpage import ClientPage
from .loginpage import LogInPage
from .registerpage import RegisterPage
from .resetpage import ResetPage
from .trackpage import TrackPage, TrackPageServer, TrackPageLocalMP
from .carpage import CarPage, CarPageServer, CarPageClient, CarPageSeason, \
    CarPageLocalMP
from .driverpage import DriverPageSinglePlayer, DriverPageServer, \
    DriverPageClient, DriverPageMP
from .optionpage import OptionPage
from .inputpage import InputPage, InputPage2, InputPage3, InputPage4
from .creditpage import CreditPage
from .roompage import RoomPage, RoomPageClient
from .numplayerspage import NumPlayersPage
from .supporterspage import SupportersPage


class MenuProps(object):

    def __init__(self, gameprops, opt_file, title_img, feed_url, site_url,
                 has_save, support_url):
        self.gameprops = gameprops
        self.opt_file = opt_file
        self.title_img = title_img
        self.feed_url = feed_url
        self.site_url = site_url
        self.has_save = has_save
        self.support_url = support_url


class YorgMenuLogic(MenuLogic):

    def on_push_page(self, page_code, args=[]):
        if page_code == 'singleplayer':
            self.eng.log('single player')
            page = SingleplayerPage(args[0])
            page.gui.attach(self.on_track_selected)
            page.gui.attach(self.on_continue)
        if page_code == 'login':
            self.eng.log('login')
            page = LogInPage(args[0])
        if page_code == 'register':
            self.eng.log('register')
            page = RegisterPage(args[0])
        if page_code == 'reset':
            self.eng.log('reset')
            page = ResetPage(args[0])
        if page_code == 'single_race':
            self.eng.log('single race')
            page = TrackPage(args[0])
            page.gui.attach(self.on_track_selected)
        if page_code == 'localmp':
            self.eng.log('local multiplayer')
            page = NumPlayersPage(args[0])
            page.gui.attach(self.on_nplayers)
        if page_code == 'multiplayer':
            self.eng.log('multiplayer')
            page = MultiplayerPage(args[0])
        if page_code == 'online':
            self.eng.log('online')
            page = OnlinePage(args[0])
        if page_code == 'onlineplay':
            self.eng.log('onlineplay')
            page = OnlinePlayPage(args[0])
            page.gui.attach(self.on_create_room)
        if page_code == 'client':
            self.eng.log('client')
            page = ClientPage(args[0])
            page.gui.attach(self.on_create_room_client)
        if page_code == 'trackpageserver':
            self.eng.log('track page server')
            page = TrackPageServer(args[0], args[1])
            page.gui.attach(self.on_track_selected)
        if page_code == 'trackpagelocalmp':
            self.eng.log('track page local multiplayer')
            page = TrackPageLocalMP(args[0])
            page.gui.attach(self.on_track_selected_lmp)
        if page_code == 'new_season':
            self.eng.log('new season')
            page = CarPageSeason(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected_season)
        if page_code == 'car_page':
            self.eng.log('car page')
            page = CarPage(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected)
        if page_code == 'carpageserver':
            self.eng.log('car page server')
            #page = CarPageServer(args[0], self.mediator.track, self.yorg_client)
            page = CarPageClient(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected)
        if page_code == 'carpagelocalmp':
            self.eng.log('car page local multiplayer')
            page = CarPageLocalMP(args[0], self.mediator.track, self.mediator.nplayers)
            page.gui.attach(self.on_car_selected)
        if page_code == 'carpageclient':
            self.eng.log('car page client')
            page = CarPageClient(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected)
        if page_code == 'driver_page':
            self.eng.log('driver page')
            page = DriverPageSinglePlayer(args[0], args[1], args[2])
            page.gui.attach(self.on_driver_selected)
        if page_code == 'driver_page_mp':
            self.eng.log('driver page multiplayer')
            page = DriverPageMP(args[0], args[1], args[2], self.mediator.nplayers)
            page.gui.attach(self.on_driver_selected_mp)
        if page_code == 'driverpageserver':
            self.eng.log('driver page server')
            page = DriverPageServer(args[0], args[1], args[2])
            page.gui.attach(self.on_driver_selected_server)
        if page_code == 'driverpageclient':
            self.eng.log('driver page client')
            page = DriverPageClient(args[0], args[1], args[2])
            page.gui.attach(self.on_driver_selected)
            page.gui.attach(self.on_car_start_client)
        if page_code == 'options':
            self.eng.log('options')
            page = OptionPage(self.mediator.gui.menu_props, args[0])
        if page_code == 'input':
            self.eng.log('input')
            page = InputPage(
                self.mediator.gui.menu_props, args[0], args[1])
        if page_code == 'input2':
            self.eng.log('input2')
            page = InputPage2(self.mediator.gui.menu_props, args[0], args[1])
        if page_code == 'input3':
            self.eng.log('input3')
            page = InputPage3(self.mediator.gui.menu_props, args[0], args[1])
        if page_code == 'input4':
            self.eng.log('input4')
            page = InputPage4(self.mediator.gui.menu_props, args[0], args[1])
        if page_code == 'credits':
            self.eng.log('credits')
            page = CreditPage(self.mediator.gui.menu_props)
        if page_code == 'supporters':
            self.eng.log('supporters')
            page = SupportersPage(self.mediator.gui.menu_props)
        self.push_page(page)

    def on_srv_quitted(self):
        curr_page = self.pages[-1].__class__.__name__
        if curr_page == 'RoomPageGui':
            self.on_back(curr_page)
        else:
            self.on_quit(curr_page)

    def on_removed(self):
        self.on_back(self.pages[-1].__class__.__name__)

    def on_back(self, page_code, args=[]):
        self.eng.log('back: %s' % page_code)
        if page_code == 'input_page':
            self.mediator.gui.notify('on_input_back', args[0])
        if page_code == 'options_page':
            self.mediator.gui.notify('on_options_back', args[0])
        if page_code == 'RoomPageGui':
            self.mediator.gui.notify('on_room_back')
        MenuLogic.on_back(self)

    def on_quit(self, page_code, args=[]):
        self.mediator.gui.notify('on_quit')
        MenuLogic.on_quit(self)

    def on_track_selected(self, track):
        self.mediator.track = track

    def on_track_selected_lmp(self, track):
        self.mediator.track = track

    def on_nplayers(self, num):
        self.mediator.nplayers = num

    def on_car_selected(self, car):
        self.mediator.gui.notify('on_car_selected', car)

    def on_driver_selected_server(self, name, track, car, cars):
        self.mediator.gui.notify('on_driver_selected_server', name, track, car,
                                 cars)

    def on_car_start_client(self, track, car, cars, packet):
        self.mediator.gui.notify('on_car_start_client', track, car, cars, packet)

    def on_car_selected_season(self, car):
        self.mediator.gui.notify('on_car_selected_season', car)

    def on_driver_selected(self, name, track, car):
        self.mediator.gui.notify('on_driver_selected', name, track, car)

    def on_driver_selected_mp(self, name, track, cars):
        self.mediator.gui.notify('on_driver_selected_mp', name, track, cars)

    def on_continue(self):
        self.mediator.gui.notify('on_continue')

    def on_login(self):
        self.mediator.gui.notify('on_login')

    def on_create_room(self, room, nick):
        page = RoomPage(self.mediator.gui.menu_props, room, nick)
        self.curr_room = room
        self.push_page(page)
        page.gui.attach(self.on_start_match)

    def on_start_match(self): self.notify('on_start_match')

    def on_create_room_client(self, room, nick):
        self.push_page(RoomPageClient(self.mediator.gui.menu_props, room, nick))


class YorgMenuGui(MenuGui):

    def __init__(self, mediator, menu_props):
        # every page should not manage following pages by forwarding params:
        # each page should callback the menu and it should spawn the next one
        MenuGui.__init__(self, mediator, menu_props.gameprops.menu_props)
        page = YorgMainPage(menu_props)
        page.gui.attach(self.on_login)
        page.gui.attach(self.on_logout)
        page.gui.attach(self.on_exit)
        self.eng.do_later(.01, lambda: self.mediator.logic.push_page(page))

    def on_login(self):
        self.notify('on_login')

    def on_logout(self):
        self.notify('on_logout')

    def on_exit(self):
        self.notify('on_exit')


class YorgMenu(Menu):
    gui_cls = YorgMenuGui
    logic_cls = YorgMenuLogic

    def __init__(self, menu_props):
        comps = [
            [('logic', self.logic_cls, [self])],
            [('gui', self.gui_cls, [self, menu_props])]]
        GameObject.__init__(self, comps)
        MenuFacade.__init__(self)
