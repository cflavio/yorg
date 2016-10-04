from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED, NORMAL
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from sys import exit
from racing.game.gameobject import Fsm, GameObjectMdt, Gui
from racing.game.gui.page import Page, PageArgs, transl_text
from racing.game.lang import LangMgr
from racing.game.dictfile import DictFile
from racing.game.network.server import Server
from racing.game.network.client import Client, ClientError
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGui import DirectEntry


class NetMsgs:

    track_selected = 0
    car_request = 1
    car_confirm = 2
    car_deny = 3
    car_selection = 4
    car_deselection = 5
    start_race = 6


class MainPage(Page, DirectObject):

    def build(self, fsm):
        page_args = self.gui.page_args
        menu_data = [('Single Player', _('Single Player'), lambda: fsm.demand('Singleplayer')),
                     ('Multiplayer', _('Multiplayer'), lambda: fsm.demand('Multiplayer')),
                     ('Options', _('Options'), lambda: fsm.demand('Options')),
                     ('Credits', _('Credits'), lambda: fsm.demand('Credits')),
                     ('Quit', _('Quit'), self.on_exit)]
        self.accept('escape-up', self.on_exit)
        self.gui.widgets = [
            DirectButton(
                text='', scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=menu[2], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(self.gui.widgets):
            transl_text(wdg, menu_data[i][0])
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')

    def on_exit(self):
        if game.options['open_browser_at_exit']:
            eng.open_browser('http://www.ya2.it')
        exit()


class SingleplayerPage(Page):

    def build(self, fsm):
        page_args = self.gui.page_args
        game.ranking = None
        def on_continue():
            game.ranking = game.options['last_ranking']
            game.fsm.demand('Loading')
        def on_tournament():
            game.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
            fsm.demand('Cars', 'tracks/track_prototype')
        menu_data = [
            ('Single race', lambda: fsm.demand('Tracks')),
            ('New tournament', on_tournament),
            ('Continue tournament', on_continue)]
        self.gui.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=menu[1], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        if 'last_ranking' not in game.options.dct:
            self.gui.widgets[-1]['state'] = DISABLED
            self.gui.widgets[-1].setAlphaScale(.25)
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')


class MultiplayerPage(Page):

    def build(self, fsm):
        page_args = self.gui.page_args
        menu_data = [
            ('Server', lambda: fsm.demand('Server')),
            ('Client', lambda: fsm.demand('Client'))]
        self.gui.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=menu[1], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')


class ServerPage(Page):

    def build(self, fsm):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('ya2.it', 0))
        local_addr = s.getsockname()[0]
        from json import load
        from urllib2 import urlopen
        public_addr = load(urlopen('http://httpbin.org/ip'))['origin']
        addr = local_addr + ' - ' + public_addr
        self.gui.widgets = [
            OnscreenText(text=addr, scale=.12, pos=(0, .4),
                         font=self.gui.font, fg=(.75, .75, .75, 1))]
        self.conn_txt = OnscreenText(scale=.12,
                         pos=(0, .2), font=self.gui.font, fg=(.75, .75, .75, 1))
        self.gui.widgets += [self.conn_txt]
        page_args = self.gui.page_args
        self.gui.widgets += [
            DirectButton(
                text=_('Start'), scale=.2, pos=(0, 1, -.5),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=self.start, extraArgs=[fsm],
                frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')
        game.logic.srv = Server(self.process_msg, self.process_connection)

    def process_msg(self, data_lst):
        print data_lst

    def process_connection(self, client_address):
        eng.log_mgr.log('connection from ' + client_address)
        self.conn_txt.setText(_('connection from ') + client_address)

    def start(self, fsm):
        fsm.demand('Tracks')


class ClientPage(Page):

    def build(self, fsm):
        self.fsm = fsm
        self.gui.widgets = [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=self.gui.font, fg=(.75, .75, .75, 1))]
        transl_text(self.gui.widgets[0], _('Client'))
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=self.gui.font, width=12,
            frameColor=self.gui.page_args.btn_color,
            initialText='insert the server address')
        self.ent.onscreenText['fg'] = (.75, .75, .75, 1)
        self.gui.widgets += [self.ent]
        page_args = self.gui.page_args
        self.gui.widgets += [
            DirectButton(
                text=_('Connect'), scale=.2, pos=(0, 1, -.2),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=self.connect, frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')

    def connect(self):
        try:
            print self.ent.get()
            game.logic.client = Client(self.process_msg, self.ent.get())
            self.gui.widgets += [
                OnscreenText(text=_('Waiting for the server'), scale=.12,
                             pos=(0, -.5), font=self.gui.font, fg=(.75, .75, .75, 1))]
        except ClientError:
            txt = OnscreenText(_('Error'), fg=(1, 0, 0, 1), scale=.5)
            taskMgr.doMethodLater(5.0, lambda tsk: txt.destroy(), 'destroy error text')

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            eng.log_mgr.log('track selected: ' + data_lst[1])
            self.fsm.demand('Cars', 'tracks/track_' + data_lst[1])


class OptionPage(Page):

    def build(self):
        font, page_args = self.gui.font, self.gui.page_args
        conf = game.options

        lang_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .5),
                               text_fg=(.75, .75, .75, 1),
                               text_font=font, text_align=TextNode.ARight)
        transl_text(lang_lab, 'Language')
        self.__lang_opt = DirectOptionMenu(
            text='', scale=.12, items=eng.lang_mgr.languages, pos=(.2, 1, .5),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_scale=.85, item_text_font=font,
            text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=conf['lang'],
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=self.__change_lang,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        vol_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .3),
                              text_font=font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        transl_text(vol_lab, 'Volume')
        self.__vol_slider = DirectSlider(
            pos=(.47, 0, .33), scale=.47, value=conf['volume'],
            frameColor=page_args.btn_color, thumb_frameColor=(.4, .4, .4, 1))

        fullscreen_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .1),
                                     text_font=font, text_fg=(.75, .75, .75, 1),
                                     text_align=TextNode.ARight)
        transl_text(fullscreen_lab, 'Fullscreen')
        self.__fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .12), text='', scale=.12, text_font=self.gui.font,
            text_fg=(.75, .75, .75, 1), frameColor=page_args.btn_color,
            indicatorValue=conf['fullscreen'],
            indicator_frameColor=page_args.btn_color,
            command=eng.gui_mgr.toggle_fullscreen,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        res_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.1),
                              text_font=font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        transl_text(res_lab, 'Resolution')
        if conf['resolution']:
            curr_res = conf['resolution'].replace(' ', 'x')
        else:
            curr_res =  str(eng.win.getXSize())+'x'+str(base.win.getYSize())
        self.__res_opt = DirectOptionMenu(
            text='', scale=.08, items=eng.gui_mgr.resolutions, pos=(.2, 1, -.1),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_fg=(.75, .75, .75, 1),
            item_text_font=font, item_text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=eng.gui_mgr.closest_res,
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=eng.gui_mgr.set_resolution,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        aa_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.3),
                            text_font=font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ARight)
        transl_text(aa_lab, 'Antialiasing')
        aa_next_lab = DirectLabel(text='', scale=.08, pos=(.2, 1, -.3),
                            text_font=font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ALeft)
        transl_text(aa_next_lab, '(from the next execution)')
        self.__aa_cb = DirectCheckButton(
            pos=(.12, 1, -.27), text='', scale=.12, text_font=self.gui.font,
            frameColor=page_args.btn_color,
            indicatorValue=conf['aa'],
            indicator_frameColor=page_args.btn_color,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        browser_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.5),
                            text_font=font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ARight)
        transl_text(browser_lab, "See Ya2's news at exit")
        self.__browser_cb = DirectCheckButton(
            pos=(.12, 1, -.47), text='', scale=.12, text_font=self.gui.font,
            frameColor=page_args.btn_color,
            indicatorValue=conf['open_browser_at_exit'],
            indicator_frameColor=page_args.btn_color,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'),
            command=self.on_browser)

        if base.appRunner and base.appRunner.dom:
            fullscreen_lab['text_fg'] = (.75, .75, .75, 1)
            self.__fullscreen_cb['state'] = DISABLED

            self.__res_opt['text_fg'] = (.75, .75, .75, 1)
            self.__res_opt['state'] = DISABLED

        self.gui.widgets = [
            lang_lab, self.__lang_opt, vol_lab, self.__vol_slider,
            fullscreen_lab, self.__fullscreen_cb, res_lab, self.__res_opt,
            aa_lab, self.__aa_cb, aa_next_lab, browser_lab, self.__browser_cb]
        idx = eng.lang_mgr.lang_codes.index(conf['lang'])
        self.__change_lang(eng.lang_mgr.languages[idx])
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')

    def on_browser(self, val):
        txt = _('Please, really consider enabling this option to see our news.\nWe hope you will find interesting stuff there.\nMoreover, this is how we can keep Yorg free.')
        if not val:
            dial = OkDialog(dialogName="Ya2's news", text=txt, frameColor=self.page_args.dial_color)
            dial['command'] = lambda val: dial.cleanup()  # it destroys too

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
        conf['lang'] = eng.lang_mgr.languages[self.__lang_opt.selectedIndex][:2].lower()
        conf['volume'] = self.__vol_slider.getValue()
        conf['fullscreen'] = self.__fullscreen_cb['indicatorValue']
        conf['resolution'] = self.__res_opt.get().replace('x', ' ')
        conf['aa'] = self.__aa_cb['indicatorValue']
        conf['open_browser_at_exit'] = self.__browser_cb['indicatorValue']
        conf['multithreaded_render'] = game.options['multithreaded_render']
        conf['car'] = car
        conf['track'] = track
        conf.store()

    def update_texts(self):
        self.gui.update_texts()
        curr_lang = eng.lang_mgr.curr_lang
        self.__lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.lang_mgr.set_lang(lang_dict[arg])
        self.update_texts()


class TrackPage(Page):

    def build(self, fsm):
        page_args = self.gui.page_args
        def on_track(track):
            fsm.demand('Cars', 'tracks/track_' + track)
            if hasattr(game.logic, 'srv') and game.logic.srv:
                game.logic.srv.send([NetMsgs.track_selected, track])
        menu_data = [
            ('Desert', on_track, ['desert']),
            ('Prototype', on_track, ['prototype'])]
        self.gui.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=menu[1], extraArgs=menu[2],
                frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')


class CarPage(Page):

    def build(self, game_fsm, track_path):
        page_args = self.gui.page_args
        self.track_path = track_path
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
        self.gui.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.gui.font, frameColor=page_args.btn_color,
                command=menu[1], extraArgs=menu[2],
                frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        self.current_cars = {}
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')

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


class CreditPage(Page):

    def build(self):
        self.gui.widgets = [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=self.gui.font, fg=(.75, .75, .75, 1))]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        transl_text(self.gui.widgets[0], text)
        self.gui.build(
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav',
            'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')


class _Gui(Gui):
    """ Definition of the MenuGui Class """

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        main_args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), False, True, True, '', (.9, .9, .9, .8))
        args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), True, False, False, 'Main', (.9, .9, .9, .8))
        car_args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), True, False, False, 'Tracks', (.95, .95, .95, .99))
        self.main_page = MainPage(main_args)
        self.singleplayer_page = SingleplayerPage(args)
        self.multiplayer_page = MultiplayerPage(args)
        self.server_page = ServerPage(args)
        self.client_page = ClientPage(args)
        self.track_page = TrackPage(args)
        self.car_page = CarPage(car_args)
        self.option_page = OptionPage(args)
        self.credit_page = CreditPage(args)


class _Fsm(Fsm):
    """ Definition of the DeflectorFSM Class """

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Main': ['Singleplayer', 'Multiplayer', 'Options', 'Credits'],
            'Singleplayer': ['Main', 'Tracks', 'Cars'],
            'Multiplayer': ['Main', 'Server', 'Client'],
            'Server': ['Main', 'Tracks'],
            'Client': ['Main', 'Cars'],
            'Tracks': ['Main', 'Cars'],
            'Cars': ['Main', 'Tracks'],
            'Options': ['Main'],
            'Credits': ['Main']}

    def enterMain(self):
        self.mdt.gui.main_page.build(self.mdt.fsm)

    def exitMain(self):
        self.mdt.gui.main_page.destroy()

    def enterSingleplayer(self):
        self.mdt.gui.singleplayer_page.build(self.mdt.fsm)

    def exitSingleplayer(self):
        self.mdt.gui.singleplayer_page.destroy()

    def enterMultiplayer(self):
        self.mdt.gui.multiplayer_page.build(self.mdt.fsm)

    def exitMultiplayer(self):
        self.mdt.gui.multiplayer_page.destroy()

    def enterServer(self):
        self.mdt.gui.server_page.build(self.mdt.fsm)

    def exitServer(self):
        self.mdt.gui.server_page.destroy()

    def enterClient(self):
        self.mdt.gui.client_page.build(self.mdt.fsm)

    def exitClient(self):
        self.mdt.gui.client_page.destroy()

    def enterTracks(self):
        self.mdt.gui.track_page.build(self.mdt.fsm)

    def exitTracks(self):
        self.mdt.gui.track_page.destroy()

    def enterCars(self, track_path):
        self.mdt.gui.car_page.build(self.mdt.game_fsm, track_path)

    def exitCars(self):
        self.mdt.gui.car_page.destroy()

    def enterOptions(self):
        self.mdt.gui.option_page.build()

    def exitOptions(self):
        self.mdt.gui.option_page.destroy()

    def enterCredits(self):
        self.mdt.gui.credit_page.build()

    def exitCredits(self):
        self.mdt.gui.credit_page.destroy()


class Menu(GameObjectMdt):
    gui_cls = _Gui
    fsm_cls = _Fsm

    def __init__(self, fsm):
        self.game_fsm = fsm
        GameObjectMdt.__init__(self)
        self.fsm.demand('Main')
