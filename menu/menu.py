from logging import info
from yyagl.engine.gui.menu import Menu, MenuLogic, MenuGui, MenuFacade
from yyagl.gameobject import GameObject
from yyagl.dictfile import DctFile
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
from .inputselpage import InputSelPage
from .inputpage import InputPageKeyboard, InputPage2Keyboard, \
    InputPage3Keyboard, InputPage4Keyboard, InputPageJoystick, \
    InputPage2Joystick, InputPage3Joystick, InputPage4Joystick
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

    def __init__(self, mediator):
        MenuLogic.__init__(self, mediator)
        self.uid_srv = None
        self.players = None
        self.players_mp = None
        self.players_omp = None

    def on_push_page(self, page_code, args=[]):
        if page_code == 'singleplayer':
            info('single player')
            page = SingleplayerPage(args[0])
            page.gui.attach(self.on_single_race)
            page.gui.attach(self.on_start_season)
            page.gui.attach(self.on_track_selected)
            page.gui.attach(self.on_continue)
        if page_code == 'login':
            info('login')
            page = LogInPage(args[0])
            page.gui.attach(self.on_login_page)
        if page_code == 'register':
            info('register')
            page = RegisterPage(args[0])
        if page_code == 'reset':
            info('reset')
            page = ResetPage(args[0])
        if page_code == 'single_race':
            info('single race')
            page = TrackPage(args[0])
            page.gui.attach(self.on_track_selected)
        if page_code == 'localmp':
            info('local multiplayer')
            page = NumPlayersPage(args[0])
            page.gui.attach(self.on_nplayers)
        if page_code == 'multiplayer':
            info('multiplayer')
            page = MultiplayerPage(args[0])
            page.gui.attach(self.on_start_local_mp)
        if page_code == 'online':
            info('online')
            page = OnlinePage(args[0])
        if page_code == 'onlineplay':
            info('onlineplay')
            page = OnlinePlayPage(args[0])
            page.gui.attach(self.on_create_room)
            page.gui.attach(self.on_start_mp_server)
            page.gui.attach(self.on_start_mp_client)
        if page_code == 'client':
            info('client')
            page = ClientPage(args[0])
            page.gui.attach(self.on_create_room_client)
        if page_code == 'trackpageserver':
            info('track page server')
            page = TrackPageServer(args[0], args[1])
            page.gui.attach(self.on_track_selected)
        if page_code == 'trackpagelocalmp':
            info('track page local multiplayer')
            page = TrackPageLocalMP(args[0])
            page.gui.attach(self.on_track_selected_lmp)
        if page_code == 'new_season':
            info('new season')
            page = CarPageSeason(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected_season)
        if page_code == 'car_page':
            info('car page')
            page = CarPage(args[0], self.mediator.track)
            page.gui.attach(self.on_car_selected)
        if page_code == 'carpageserver':
            info('car page server')
            #page = CarPageServer(args[0], self.mediator.track, self.yorg_client)
            page = CarPageClient(args[0], self.mediator.track, self.uid_srv)
            page.gui.attach(self.on_car_selected)
            page.gui.attach(self.on_car_selected_omp_srv)
            page.gui.attach(self.on_car_selected_omp_client)
        if page_code == 'carpagelocalmp':
            info('car page local multiplayer')
            page = CarPageLocalMP(args[0], self.mediator.track, self.mediator.nplayers)
            page.gui.attach(self.on_car_selected_mp)
        if page_code == 'carpageclient':
            info('car page client')
            page = CarPageClient(args[0], self.mediator.track, self.uid_srv)
            page.gui.attach(self.on_car_selected)
            page.gui.attach(self.on_car_selected_omp_client)
        if page_code == 'driver_page':
            info('driver page')
            page = DriverPageSinglePlayer(args[0], args[1], args[2], self.players)
            page.gui.attach(self.on_driver_selected)
        if page_code == 'driver_page_mp':
            info('driver page multiplayer')
            page = DriverPageMP(args[0], args[1], args[2], self.mediator.nplayers, self.players_mp)
            page.gui.attach(self.on_driver_selected_mp)
        if page_code == 'driverpageserver':
            info('driver page server')
            page = DriverPageServer(args[0], args[1], args[2], args[3])
            page.gui.attach(self.on_driver_selected_server)
        if page_code == 'driverpageclient':
            info('driver page client')
            page = DriverPageClient(args[0], args[1], args[2], self.uid_srv, self.players_omp)
            page.gui.attach(self.on_driver_selected)
            page.gui.attach(self.on_car_start_client)
        if page_code == 'options':
            info('options')
            page = OptionPage(self.mediator.gui.menu_props, args[0])
        if page_code == 'inputsel':
            info('inputsel')
            page = InputSelPage(self.mediator.gui._menu_props, self.mediator.menu_props.opt_file, args[0], args[1])
            #self.mediator.gui.menu_props, args[0], args[1])
        if page_code == 'input1keyboard':
            info('input1keyboard')
            page = InputPageKeyboard(
                self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, args[0])
        if page_code == 'input1joystick':
            info('input1joystick')
            page = InputPageJoystick(
                self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, args[0])
        if page_code == 'input2keyboard':
            info('input2keyboard')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage2Keyboard(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['keys'])
        if page_code == 'input2joystick':
            info('input2joystick')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage2Joystick(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['joystick'])
        if page_code == 'input3keyboard':
            info('input3keyboard')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage3Keyboard(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['keys'])
        if page_code == 'input3joystick':
            info('input3joystick')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage3Joystick(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['joystick'])
        if page_code == 'input4keyboard':
            info('input4keyboard')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage4Keyboard(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['keys'])
        if page_code == 'input4joystick':
            info('input4joystick')
            self.mediator.menu_props.opt_file['settings'] = DctFile.deepupdate(self.mediator.menu_props.opt_file['settings'], args[1])
            self.mediator.menu_props.opt_file.store()
            page = InputPage4Joystick(self.mediator.gui.menu_props, self.mediator.menu_props.opt_file, self.mediator.menu_props.opt_file['settings']['joystick'])
        if page_code == 'credits':
            info('credits')
            page = CreditPage(self.mediator.gui.menu_props)
        if page_code == 'supporters':
            info('supporters')
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
        info('back: %s' % page_code)
        if page_code.startswith('input_page'):
            self.mediator.gui.notify('on_input_back', args[0])
            if page_code in ['input_page' + str(n) for n in range(1, 5)]: self.pages[-2].gui.update_keys()
        if page_code == 'options_page':
            self.mediator.gui.notify('on_options_back', args[0])
        if page_code == 'RoomPageGui':
            self.mediator.gui.notify('on_room_back')
        MenuLogic.on_back(self)

    def on_quit(self, page_code, args=[]):
        self.mediator.gui.notify('on_quit')
        MenuLogic.on_quit(self)

    def on_track_selected(self, track):
        self.mediator.gui.notify('on_track_selected')
        self.mediator.track = track

    def on_track_selected_lmp(self, track):
        self.mediator.track = track
        self.mediator.gui.notify('on_track_selected_mp')

    def on_nplayers(self, num):
        self.mediator.nplayers = num

    def on_single_race(self):
        self.mediator.gui.notify('on_single_race')

    def on_start_season(self):
        self.mediator.gui.notify('on_start_season')

    def on_start_local_mp(self):
        self.mediator.gui.notify('on_start_local_mp')

    def on_start_mp_server(self):
        self.mediator.gui.notify('on_start_mp_server')

    def on_start_mp_client(self):
        self.mediator.gui.notify('on_start_mp_client')

    def on_car_selected(self, car):
        self.mediator.gui.notify('on_car_selected', car)

    def on_car_selected_mp(self, car, player_idx):
        self.mediator.gui.notify('on_car_selected_mp', car, player_idx)

    def on_car_selected_omp_srv(self, car):
        self.mediator.gui.notify('on_car_selected_omp_srv', car)

    def on_car_selected_omp_client(self, car):
        self.mediator.gui.notify('on_car_selected_omp_client', car)

    def on_driver_selected_server(self, name, track, car, cars):
        self.mediator.gui.notify('on_driver_selected_server', name, track, car,
                                 cars)

    def on_car_start_client(self, track, car, cars, packet):
        self.mediator.gui.notify('on_car_start_client', track, car, cars, packet, self.curr_room)

    def on_car_selected_season(self, car):
        self.mediator.gui.notify('on_car_selected_season', car)

    def on_driver_selected(self, name, track, car, i):
        self.mediator.gui.notify('on_driver_selected', name, track, car, i)

    def on_driver_selected_mp(self, track, players):
        self.mediator.gui.notify('on_driver_selected_mp', track, players)

    def on_continue(self):
        self.mediator.gui.notify('on_continue')

    def on_login_page(self):
        self.mediator.gui.notify('on_login')

    def on_login(self):
        self.mediator.gui.notify('on_login')

    def on_create_room(self, room, nick):
        page = RoomPage(self.mediator.gui.menu_props, room, nick, nick)
        self.curr_room = room
        self.push_page(page)
        page.gui.attach(self.on_start_match)

    def on_start_match(self, room_name):
        self.curr_room = room_name
        self.notify('on_start_match')

    def on_create_room_client(self, room, nick, uid_srv):
        self.uid_srv = uid_srv
        page = RoomPageClient(self.mediator.gui.menu_props, room, nick, uid_srv)
        self.push_page(page)
        page.gui.attach(self.on_start_match_client_page)
        page.gui.attach(self.on_srv_quitted)

    def on_start_match_client_page(self, track, room_name):
        self.curr_room = room_name
        self.notify('on_start_match_client_menu', track)


class YorgMenuGui(MenuGui):

    def __init__(self, mediator, menu_props):
        # every page should not manage following pages by forwarding params:
        # each page should callback the menu and it should spawn the next one
        MenuGui.__init__(self, mediator, menu_props.gameprops.menu_props)
        self._menu_props = menu_props
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
        self.menu_props = menu_props
        GameObject.__init__(self)
        self.logic = self.logic_cls(self)
        self.gui = self.gui_cls(self, menu_props)
        MenuFacade.__init__(self)
