from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from sys import exit
from ya2.gameobject import Fsm, GameObjectMdt, Gui
from ya2.gui import Page, PageArgs, transl_text
from ya2.engine import LangMgr, OptionMgr


class MainPage(Page):

    def create(self, fsm):
        page_args = self.page_args
        menu_data = [('Play', _('Play'), lambda: fsm.demand('Tracks')),
                     ('Options', _('Options'), lambda: fsm.demand('Options')),
                     ('Credits', _('Credits'), lambda: fsm.demand('Credits')),
                     ('Quit', _('Quit'), lambda: exit())]
        self.widgets = [
            DirectButton(
                text='', scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.font, frameColor=page_args.btn_color,
                command=menu[2], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        for i, wdg in enumerate(self.widgets):
            transl_text(wdg, menu_data[i][0], menu_data[i][1])
        Page.create(self)


class OptionPage(Page):

    def create(self):
        font, page_args = self.font, self.page_args
        conf = OptionMgr.get_options()

        lang_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .4),
                               text_fg=(.75, .75, .75, 1),
                               text_font=font, text_align=TextNode.ARight)
        transl_text(lang_lab, 'Language', _('Language'))
        self.__lang_opt = DirectOptionMenu(
            text='', scale=.12, items=LangMgr.languages, pos=(.2, 1, .4),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_scale=.85, item_text_font=font,
            text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=conf['lang'],
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=self.__change_lang,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        vol_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, .2),
                              text_font=font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        transl_text(vol_lab, 'Volume', _('Volume'))
        self.__vol_slider = DirectSlider(
            pos=(.47, 0, .23), scale=.47, value=conf['volume'],
            frameColor=page_args.btn_color, thumb_frameColor=(.4, .4, .4, 1))

        fullscreen_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, 0),
                                     text_font=font, text_fg=(.75, .75, .75, 1),
                                     text_align=TextNode.ARight)
        transl_text(fullscreen_lab, 'Fullscreen', _('Fullscreen'))
        self.__fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .03), text='', scale=.12, text_font=self.font,
            text_fg=(.75, .75, .75, 1), frameColor=page_args.btn_color,
            indicatorValue=conf['fullscreen'],
            indicator_frameColor=page_args.btn_color,
            command=eng.toggle_fullscreen,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        res_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.2),
                              text_font=font, text_fg=(.75, .75, .75, 1),
                              text_align=TextNode.ARight)
        transl_text(res_lab, 'Resolution', _('Resolution'))
        if conf['resolution']:
            curr_res = conf['resolution'].replace(' ', 'x')
        else:
            curr_res =  str(eng.win.getXSize())+'x'+str(base.win.getYSize())
        self.__res_opt = DirectOptionMenu(
            text='', scale=.12, items=eng.resolutions, pos=(.2, 1, -.2),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_fg=(.75, .75, .75, 1), text_scale=.85,
            item_text_font=font, item_text_fg=(.75, .75, .75, 1),
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=eng.closest_res,
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=eng.set_resolution,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        aa_lab = DirectLabel(text='', scale=.12, pos=(-.1, 1, -.4),
                            text_font=font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ARight)
        transl_text(aa_lab, 'Antialiasing',
                    _('Antialiasing'))
        aa_next_lab = DirectLabel(text='', scale=.08, pos=(.2, 1, -.4),
                            text_font=font, text_fg=(.75, .75, .75, 1),
                            text_align=TextNode.ALeft)
        transl_text(aa_next_lab, '(from the next execution)',
                    _('(from the next execution)'))
        self.__aa_cb = DirectCheckButton(
            pos=(.12, 1, -.37), text='', scale=.12, text_font=self.font,
            frameColor=page_args.btn_color,
            indicatorValue=conf['aa'],
            indicator_frameColor=page_args.btn_color,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        if base.appRunner and base.appRunner.dom:
            fullscreen_lab['text_fg'] = (.75, .75, .75, 1)
            self.__fullscreen_cb['state'] = DISABLED

            self.__res_opt['text_fg'] = (.75, .75, .75, 1)
            self.__res_opt['state'] = DISABLED

        self.widgets = [
            lang_lab, self.__lang_opt, vol_lab, self.__vol_slider,
            fullscreen_lab, self.__fullscreen_cb, res_lab, self.__res_opt,
            aa_lab, self.__aa_cb, aa_next_lab]
        self.__change_lang(LangMgr.languages[conf['lang']])
        Page.create(self)

    def on_back(self):
        conf = {
            'lang': self.__lang_opt.selectedIndex,
            'volume': self.__vol_slider.getValue(),
            'fullscreen': self.__fullscreen_cb['indicatorValue'],
            'resolution': self.__res_opt.get().replace('x', ' '),
            'aa': self.__aa_cb['indicatorValue']}
        OptionMgr.set_options(conf)

    def update_texts(self):
        Page.update_texts(self)
        curr_lang = eng.lang_mgr.curr_lang
        self.__lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.lang_mgr.set_lang(lang_dict[arg])
        self.update_texts()


class TrackPage(Page):

    def create(self, fsm):
        page_args = self.page_args
        menu_data = [
            ('Desert', lambda: fsm.demand('Cars', 'tracks/track_desert')),
            ('Prototype', lambda: fsm.demand('Cars', 'tracks/track_prototype'))]
        self.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.font, frameColor=page_args.btn_color,
                command=menu[1], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        Page.create(self)


class CarPage(Page):

    def create(self, game_fsm, track_path):
        page_args = self.page_args
        menu_data = [
            ('Kronos', lambda: game_fsm.demand('Play', track_path, 'kronos')),
            ('Red', lambda: game_fsm.demand('Play', track_path, 'red'))]
        self.widgets = [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=self.font, frameColor=page_args.btn_color,
                command=menu[1], frameSize=page_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        Page.create(self)


class CreditPage(Page):

    def create(self):
        self.widgets = [
            OnscreenText(text='', scale=.12, pos=(0, .4),
                         font=self.font, fg=(.75, .75, .75, 1))]
        flavio = _('Code')+': Flavio Calva'
        luca = _('Art')+': Luca Quartero'
        text = '\n\n'.join([flavio, luca])
        transl_text(self.widgets[0], text, text)
        Page.create(self)


class _Gui(Gui):
    """ Definition of the MenuGui Class """

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        main_args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), False, True, True, '')
        args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), True, False, False, 'Main')
        car_args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), True, False, False, 'Tracks')
        self.main_page = MainPage(main_args)
        self.track_page = TrackPage(args)
        self.car_page = CarPage(car_args)
        self.option_page = OptionPage(args)
        self.credit_page = CreditPage(args)


class _Fsm(Fsm):
    """ Definition of the DeflectorFSM Class """

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Main': ['Tracks', 'Options', 'Credits'],
            'Tracks': ['Main', 'Cars'],
            'Cars': ['Main', 'Tracks'],
            'Options': ['Main'],
            'Credits': ['Main']}

    def enterMain(self):
        self.mdt.gui.main_page.create(self.mdt.fsm)

    def exitMain(self):
        self.mdt.gui.main_page.destroy()

    def enterTracks(self):
        self.mdt.gui.track_page.create(self.mdt.fsm)

    def exitTracks(self):
        self.mdt.gui.track_page.destroy()

    def enterCars(self, track_path):
        self.mdt.gui.car_page.create(self.mdt.game_fsm, track_path)

    def exitCars(self):
        self.mdt.gui.car_page.destroy()

    def enterOptions(self):
        self.mdt.gui.option_page.create()

    def exitOptions(self):
        self.mdt.gui.option_page.destroy()

    def enterCredits(self):
        self.mdt.gui.credit_page.create()

    def exitCredits(self):
        self.mdt.gui.credit_page.destroy()


class Menu(GameObjectMdt):
    gui_cls = _Gui
    fsm_cls = _Fsm

    def __init__(self, fsm):
        self.game_fsm = fsm
        GameObjectMdt.__init__(self)
        self.fsm.demand('Main')
