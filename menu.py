from sys import exit
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED, NORMAL
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGui import DirectEntry
from panda3d.core import TextNode
from racing.game.gameobject.gameobject import Fsm, GameObjectMdt, Gui
from racing.game.engine.gui.page import Page, PageEvent, PageGui
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.menu import MenuArgs, Menu
from racing.game.engine.lang import LangMgr
from racing.game.dictfile import DictFile
from racing.game.engine.network.server import Server
from racing.game.engine.network.client import Client, ClientError


class NetMsgs:

    track_selected = 0
    car_request = 1
    car_confirm = 2
    car_deny = 3
    car_selection = 4
    car_deselection = 5
    start_race = 6


class YorgMainPageGui(MainPageGui):

    def build(self):
        menu_data = [('Single Player', _('Single Player'), lambda: self.menu.logic.push_page(SingleplayerPage(self.menu))),
                     ('Multiplayer', _('Multiplayer'), lambda: self.menu.logic.push_page(MultiplayerPage(self.menu))),
                     ('Options', _('Options'), lambda: self.menu.logic.push_page(OptionPage(self.menu))),
                     ('Credits', _('Credits'), lambda: self.menu.logic.push_page(CreditPage(self.menu))),
                     ('Quit', _('Quit'), lambda: messenger.send('window-closed'))]
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.widgets += [
            DirectButton(
                text='', scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[2], frameSize=menu_args.btn_size,
                rolloverSound=menu_gui.rollover,
                clickSound=menu_gui.click)
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(self.widgets):
            PageGui.transl_text(wdg, menu_data[i][0])
        MainPageGui.build(self)


class YorgMainPage(MainPage):
    '''This class models a page.'''
    gui_cls = YorgMainPageGui


class SingleplayerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        game.ranking = None
        def on_continue():
            game.ranking = game.options['last_ranking']
            game.fsm.demand('Loading')
        def on_tournament():
            game.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
            self.menu.track = 'prototype'
            self.menu.logic.push_page(CarPage(self.menu))
        menu_data = [
            ('Single race', lambda: self.menu.logic.push_page(TrackPage(self.menu))),
            ('New tournament', on_tournament),
            ('Continue tournament', on_continue)]
        self.widgets += [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        if 'last_ranking' not in game.options.dct:
            self.widgets[-1]['state'] = DISABLED
            self.widgets[-1].setAlphaScale(.25)
        PageGui.build(self)


class SingleplayerPage(Page):
    '''This class models a page.'''
    gui_cls = SingleplayerPageGui


class MultiplayerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        menu_data = [
            ('Server', lambda: self.menu.logic.push_page(ServerPage(self.menu))),
            ('Client', lambda: self.menu.logic.push_page(ClientPage(self.menu)))]
        self.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        PageGui.build(self)


class MultiplayerPage(Page):
    '''This class models a page.'''
    gui_cls = MultiplayerPageGui


class ServerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('ya2.it', 0))
        local_addr = s.getsockname()[0]
        from json import load
        from urllib2 import urlopen
        public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
        addr = local_addr + ' - ' + public_addr
        self.widgets += [
            OnscreenText(text=addr, scale=.12, pos=(0, .4),
                         font=menu_gui.font, fg=(.75, .75, .75, 1))]
        self.conn_txt = OnscreenText(scale=.12,
                         pos=(0, .2), font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [self.conn_txt]
        self.widgets += [
            DirectButton(
                text=_('Start'), scale=.2, pos=(0, 1, -.5),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=lambda: self.menu.logic.push_page(TrackPage(self.menu)),
                frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        PageGui.build(self)
        game.logic.srv = Server(self.process_msg, self.process_connection)

    def process_msg(self, data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log_mgr.log('connection from ' + client_address)
        self.conn_txt.setText(_('connection from ') + client_address)


class ServerPage(Page):
    '''This class models a page.'''
    gui_cls = ServerPageGui


class ClientPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.widgets += [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=menu_gui.font, fg=(.75, .75, .75, 1))]
        PageGui.transl_text(self.widgets[0], _('Client'))
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=menu_gui.font, width=12,
            frameColor=menu_args.btn_color,
            initialText='insert the server address')
        self.ent.onscreenText['fg'] = (.75, .75, .75, 1)
        self.widgets += [self.ent]
        self.widgets += [
            DirectButton(
                text=_('Connect'), scale=.2, pos=(0, 1, -.2),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=self.connect, frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        PageGui.build(self)

    def connect(self):
        try:
            print self.ent.get()
            game.logic.client = Client(self.process_msg, self.ent.get())
            self.widgets += [
                OnscreenText(text=_('Waiting for the server'), scale=.12,
                             pos=(0, -.5), font=menu_gui.font, fg=(.75, .75, .75, 1))]
        except ClientError:
            txt = OnscreenText(_('Error'), fg=(1, 0, 0, 1), scale=.5)
            taskMgr.doMethodLater(5.0, lambda tsk: txt.destroy(), 'destroy error text')

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            eng.log_mgr.log('track selected: ' + data_lst[1])
            self.menu_fsm.demand('Cars', 'tracks/track_' + data_lst[1])


class ClientPage(Page):
    '''This class models a page.'''
    gui_cls = ClientPageGui


class OptionEvent(PageEvent):

    def on_back(self):
        try:
            car = game.options['car']
        except KeyError:
            car = ''
        try:
            track = game.options['track']
        except KeyError:
            track = ''
        conf = game.options
        conf['lang'] = eng.lang_mgr.languages[self.mdt.gui._lang_opt.selectedIndex][:2].lower()
        conf['volume'] = self.mdt.gui._vol_slider.getValue()
        conf['fullscreen'] = self.mdt.gui._fullscreen_cb['indicatorValue']
        conf['resolution'] = self.mdt.gui._res_opt.get().replace('x', ' ')
        conf['aa'] = self.mdt.gui._aa_cb['indicatorValue']
        conf['open_browser_at_exit'] = self.mdt.gui._browser_cb['indicatorValue']
        conf['multithreaded_render'] = game.options['multithreaded_render']
        conf['car'] = car
        conf['track'] = track
        conf.store()


class OptionPageGui(PageGui):


    def build(self):
        conf = game.options
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        lang_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .5),
                               text_fg=(.75, .75, .75, 1),
                               text_font=menu_gui.font, text_align=TextNode.ARight)
        PageGui.transl_text(lang_lab, 'Language')
        self._lang_opt = DirectOptionMenu(
            text='', scale=.12, items=eng.lang_mgr.languages, pos=(.2, 1, .5),
            frameColor=menu_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=menu_gui.font, text_scale=.85, item_text_font=menu_gui.font,
            text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=conf['lang'],
            popupMarker_frameColor=menu_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=self.__change_lang,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        vol_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .3),
                              text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        PageGui.transl_text(vol_lab, 'Volume')
        self._vol_slider = DirectSlider(
            pos=(.47, 0, .33), scale=.47, value=conf['volume'],
            frameColor=menu_args.btn_color, thumb_frameColor=(.4, .4, .4, 1))

        fullscreen_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .1),
                                     text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                                     text_align=TextNode.ARight)
        PageGui.transl_text(fullscreen_lab, 'Fullscreen')
        self._fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .12), text='', scale=.12, text_font=menu_gui.font,
            text_fg=(.75, .75, .75, 1), frameColor=menu_args.btn_color,
            indicatorValue=conf['fullscreen'],
            indicator_frameColor=menu_args.btn_color,
            command=eng.gui.toggle_fullscreen,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        res_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.1),
                              text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        PageGui.transl_text(res_lab, 'Resolution')
        if conf['resolution']:
            curr_res = conf['resolution'].replace(' ', 'x')
        else:
            curr_res =  str(eng.win.getXSize())+'x'+str(base.win.getYSize())
        self._res_opt = DirectOptionMenu(
            text='', scale=.08,
            items=['x'.join([str(el_res) for el_res in res]) for res in eng.gui.resolutions],
            pos=(.2, 1, -.1),
            frameColor=menu_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
            item_text_font=menu_gui.font, item_text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem='x'.join(str(res) for res in eng.gui.closest_res),
            popupMarker_frameColor=menu_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=eng.gui.set_resolution,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        aa_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.3),
                            text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ARight)
        PageGui.transl_text(aa_lab, 'Antialiasing')
        aa_next_lab = DirectLabel(text='', scale=.08, pos=(.2, 1, -.3),
                            text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ALeft)
        PageGui.transl_text(aa_next_lab, '(from the next execution)')
        self._aa_cb = DirectCheckButton(
            pos=(.12, 1, -.27), text='', scale=.12, text_font=menu_gui.font,
            frameColor=menu_args.btn_color,
            indicatorValue=conf['aa'],
            indicator_frameColor=menu_args.btn_color,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        browser_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.5),
                            text_font=menu_gui.font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ARight)
        PageGui.transl_text(browser_lab, "See Ya2's news at exit")
        self._browser_cb = DirectCheckButton(
            pos=(.12, 1, -.47), text='', scale=.12, text_font=menu_gui.font,
            frameColor=menu_args.btn_color,
            indicatorValue=conf['open_browser_at_exit'],
            indicator_frameColor=menu_args.btn_color,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'),
            command=self.on_browser)

        if base.appRunner and base.appRunner.dom:
            fullscreen_lab['text_fg'] = (.75, .75, .75, 1)
            self.__fullscreen_cb['state'] = DISABLED

            self.__res_opt['text_fg'] = (.75, .75, .75, 1)
            self.__res_opt['state'] = DISABLED

        self.widgets += [
            lang_lab, self._lang_opt, vol_lab, self._vol_slider,
            fullscreen_lab, self._fullscreen_cb, res_lab, self._res_opt,
            aa_lab, self._aa_cb, aa_next_lab, browser_lab, self._browser_cb]
        idx = eng.lang_mgr.lang_codes.index(conf['lang'])
        self.__change_lang(eng.lang_mgr.languages[idx])
        PageGui.build(self)

    def on_browser(self, val):
        txt = _('Please, really consider enabling this option to see our news.\nWe hope you will find interesting stuff there.\nMoreover, this is how we can keep Yorg free.')
        if not val:
            dial = OkDialog(dialogName="Ya2's news", text=txt, frameColor=self.menu.gui.menu_args.dial_color)
            dial['command'] = lambda val: dial.cleanup()  # it destroys too

    def update_texts(self):
        PageGui.update_texts(self)
        curr_lang = eng.lang_mgr.curr_lang
        self._lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.lang_mgr.set_lang(lang_dict[arg])
        self.update_texts()


class OptionPage(Page):
    '''This class models a page.'''
    gui_cls = OptionPageGui
    event_cls = OptionEvent


class TrackPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        def on_track(track):
            self.menu.track = track
            self.menu.logic.push_page(CarPage(self.menu))
            if hasattr(game.logic, 'srv') and game.logic.srv:
                game.logic.srv.send([NetMsgs.track_selected, track])
        menu_data = [
            ('Desert', on_track, ['desert']),
            ('Prototype', on_track, ['prototype'])]
        self.widgets += [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], extraArgs=menu[2],
                frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        PageGui.build(self)

    def destroy(self):
        del self.menu.track
        PageGui.destroy(self)


class TrackPage(Page):
    '''This class models a page.'''
    gui_cls = TrackPageGui


class CarPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.track_path = 'tracks/track_' + self.menu.track
        if hasattr(game.logic, 'srv') and game.logic.srv:
            game.logic.srv.register_cb(self.process_srv)
            game.logic.srv.car_mapping = {}
        elif hasattr(game.logic, 'client') and game.logic.client:
            game.logic.client.register_cb(self.process_client)
        def on_car(car):
            if hasattr(game.logic, 'srv') and game.logic.srv:
                eng.log_mgr.log('car selected: ' + car)
                game.logic.srv.send([NetMsgs.car_selection, car])
                for btn in [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [car]]:
                    btn['state'] = DISABLED
                    btn.setAlphaScale(.25)
                if self in self.current_cars:
                  eng.log_mgr.log('car deselected: ' + self.current_cars[self])
                  game.logic.srv.send([NetMsgs.car_deselection, self.current_cars[self]])
                  for btn in [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [self.current_cars[self]]]:
                      btn['state'] = NORMAL
                      btn.setAlphaScale(1)
                self.current_cars[self] = car
                game.logic.srv.car_mapping['self'] = car
                self.evaluate_starting()
            elif hasattr(game.logic, 'client') and game.logic.client:
                eng.log_mgr.log('car request: ' + car)
                game.logic.client.send([NetMsgs.car_request, car])
            else:
                game.fsm.demand('Loading', self.track_path, car)
        menu_data = [
            ('Kronos', on_car, ['kronos']),
            ('Themis', on_car, ['themis']),
            ('Diones', on_car, ['diones'])]
        self.widgets += [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], extraArgs=menu[2],
                frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        self.current_cars = {}
        PageGui.build(self)

    def evaluate_starting(self):
        if all(conn in self.current_cars for conn in game.logic.srv.connections + [self]):
            packet = [NetMsgs.start_race]
            packet += [len(self.current_cars)]
            def process(k):
                return 'server' if k == self else k.getAddress().getIpString()
            for k, v in self.current_cars.items():
                packet += [process(k)]
                packet += [v]
            game.logic.srv.send(packet)
            eng.log_mgr.log('start race: ' + str(packet))
            game.fsm.demand('Loading', self.track_path, self.current_cars[self],
                            packet[2:])

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_request:
            car = data_lst[1]
            eng.log_mgr.log('car requested: ' + car)
            btn = [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [car]][0]
            if btn['state'] == DISABLED:
                game.logic.srv.send([NetMsgs.car_deny], sender)
                eng.log_mgr.log('car already selected: ' + car)
            elif btn['state'] == NORMAL:
                eng.log_mgr.log('car selected: ' + car)
                self.current_cars[sender] = car
                btn['state'] == DISABLED
                game.logic.srv.send([NetMsgs.car_confirm, car], sender)
                game.logic.srv.send([NetMsgs.car_selection, car])
                game.logic.srv.car_mapping[sender] = car
                self.evaluate_starting()

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.car_confirm:
            self.car = car = data_lst[1]
            eng.log_mgr.log('car confirmed: ' + car)
            btn = [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [car]][0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deny:
            eng.log_mgr.log('car denied')
        if data_lst[0] == NetMsgs.car_selection:
            car = data_lst[1]
            eng.log_mgr.log('car selection: ' + car)
            btn = [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [car]][0]
            btn['state'] = DISABLED
            btn.setAlphaScale(.25)
        if data_lst[0] == NetMsgs.car_deselection:
            car = data_lst[1]
            eng.log_mgr.log('car deselection: ' + car)
            btn = [wdg for wdg in self.gui.widgets if wdg.__class__ == DirectButton and wdg['extraArgs'] == [car]][0]
            btn['state'] = NORMAL
            btn.setAlphaScale(1)
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start_race: ' + str(data_lst))
            game.fsm.demand('Loading', self.track_path, self.car, data_lst[2:])


class CarPage(Page):
    '''This class models a page.'''
    gui_cls = CarPageGui


class CreditPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        self.widgets += [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=menu_gui.font, fg=(.75, .75, .75, 1))]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        PageGui.transl_text(self.widgets[0], text)
        PageGui.build(self)


class CreditPage(Page):
    '''This class models a page.'''
    gui_cls = CreditPageGui


class _Gui(Gui):
    """ Definition of the MenuGui Class """

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/zekton rg.ttf', (.75, .75, .75, 1), .12,
            (-3, 3, -.32, .88), (0, 0, 0, .2), (.9, .9, .9, .8),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(YorgMainPage(self.menu))
        #self.singleplayer_page = SingleplayerPage()
        #self.multiplayer_page = MultiplayerPage()
        #self.server_page = ServerPage()
        #self.client_page = ClientPage()
        #self.track_page = TrackPage()
        #self.car_page = CarPage()
        #self.option_page = OptionPage()
        #self.credit_page = CreditPage()

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


#class _Fsm(Fsm):
#    """ Definition of the DeflectorFSM Class """

    #def __init__(self, mdt):
    #    Fsm.__init__(self, mdt)
    #    self.defaultTransitions = {
    #        'Main': ['Singleplayer', 'Multiplayer', 'Options', 'Credits'],
    #        'Singleplayer': ['Main', 'Tracks', 'Cars'],
    #        'Multiplayer': ['Main', 'Server', 'Client'],
    #        'Server': ['Main', 'Tracks'],
    #        'Client': ['Main', 'Cars'],
    #        'Tracks': ['Main', 'Cars'],
    #        'Cars': ['Main', 'Tracks'],
    #        'Options': ['Main'],
    #        'Credits': ['Main']}

    #def enterMain(self):
    #    self.mdt.gui.main_page.build(self.mdt.fsm)

    #def exitMain(self):
    #    self.mdt.gui.main_page.destroy()

    #def enterSingleplayer(self):
    #    self.mdt.gui.singleplayer_page.build(self.mdt.fsm)

    #def exitSingleplayer(self):
    #    self.mdt.gui.singleplayer_page.destroy()

    #def enterMultiplayer(self):
    #    self.mdt.gui.multiplayer_page.build(self.mdt.fsm)

    #def exitMultiplayer(self):
    #    self.mdt.gui.multiplayer_page.destroy()

    #def enterServer(self):
    #    self.mdt.gui.server_page.build(self.mdt.fsm)

    #def exitServer(self):
    #    self.mdt.gui.server_page.destroy()

    #def enterClient(self):
    #    self.mdt.gui.client_page.build(self.mdt.fsm)

    #def exitClient(self):
    #    self.mdt.gui.client_page.destroy()

    #def enterTracks(self):
    #    self.mdt.gui.track_page.build(self.mdt.fsm)

    #def exitTracks(self):
    #    self.mdt.gui.track_page.destroy()

    #def enterCars(self, track_path):
    #    self.mdt.gui.car_page.build(self.mdt.game_fsm, track_path)

    #def exitCars(self):
    #    self.mdt.gui.car_page.destroy()

    #def enterOptions(self):
    #    self.mdt.gui.option_page.build()

    #def exitOptions(self):
    #    self.mdt.gui.option_page.destroy()

    #def enterCredits(self):
    #    self.mdt.gui.credit_page.build()

    #def exitCredits(self):
    #    self.mdt.gui.credit_page.destroy()

    #def destroy(self):
    #    Fsm.destroy(self)


class YorgMenu(GameObjectMdt):
    gui_cls = _Gui

    def __init__(self, fsm):
        self.game_fsm = fsm
        GameObjectMdt.__init__(self)
        #self.fsm.demand('Main')
