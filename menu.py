from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from sys import exit
from ya2.gameobject import Fsm, GameObjectMdt, Gui
from ya2.gui import Page, PageArgs, transl_text


class MainPage(Page):

    def create(self, game_fsm, fsm):
        page_args = self.page_args
        menu_data = [('Play', _('Play'), lambda: game_fsm.demand('Play')),
                     ('Options', _('Options'), lambda: fsm.demand('Options')),
                     ('Credits', _('Credits'), lambda: fsm.demand('Credits')),
                     ('Quit', _('Quit'), lambda: exit())]
        self.widgets = [
            DirectButton(
                text='', scale=.2, pos=(0, 1, .4-i*.28),
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

        lang_lab = DirectLabel(text='', scale=.12, pos=(-.4, 1, .4),
                               text_font=font)
        transl_text(lang_lab, 'Language', _('Language'))
        lang_list = ['en', 'it']
        self.__lang_opt = DirectOptionMenu(
            text='', scale=.12, items=['English', 'Italiano'], pos=(.4, 1, .4),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_scale=.85, item_text_font=font,
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=lang_list.index(eng.lang_mgr.curr_lang),
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=self.__change_lang,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        vol_lab = DirectLabel(text='', scale=.12, pos=(-.4, 1, .2),
                              text_font=font)
        transl_text(vol_lab, 'Volume', _('Volume'))
        vol_slider = DirectSlider(
            pos=(.68, 0, .23), scale=.47, value=1,
            frameColor=page_args.btn_color, thumb_frameColor=(.4, .4, .4, 1))

        fullscreen_lab = DirectLabel(text='', scale=.12, pos=(-.4, 1, 0),
                                     text_font=font)
        transl_text(fullscreen_lab, 'Fullscreen', _('Fullscreen'))
        fullscreen_cb = DirectCheckButton(
            pos=(.33, 1, .03), text='', scale=.12, text_font=self.font,
            frameColor=page_args.btn_color,
            indicator_frameColor=page_args.btn_color,
            command=eng.toggle_fullscreen,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        res_lab = DirectLabel(text='', scale=.12, pos=(-.4, 1, -.2),
                              text_font=font)
        transl_text(res_lab, 'Resolution', _('Resolution'))
        self.__res_opt = DirectOptionMenu(
            text='', scale=.12, items=eng.resolutions, pos=(.4, 1, -.2),
            frameColor=page_args.btn_color, frameSize=(-1.6, 5.6, -.32, .88),
            text_font=font, text_scale=.85, item_text_font=font,
            item_frameColor=(.6, .6, .6, 1), item_relief=FLAT,
            initialitem=self.__index_closest(),
            popupMarker_frameColor=page_args.btn_color, textMayChange=1,
            highlightColor=(.8, .8, .8, .2), command=eng.set_resolution,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))

        if base.appRunner and base.appRunner.dom:
            fullscreen_lab['text_fg'] = (.25, .25, .25, 1)
            fullscreen_cb['state'] = DISABLED

            self.__res_opt['text_fg'] = (.25, .25, .25, 1)
            self.__res_opt['state'] = DISABLED

        self.widgets = [
            lang_lab, self.__lang_opt, vol_lab, vol_slider, fullscreen_lab,
            fullscreen_cb, res_lab, self.__res_opt]
        Page.create(self)

    def __index_closest(self):
        def split_res(res):
            return [int(v) for v in res.split('x')]

        def distance(res):
            curr_res, res = split_res(eng.resolution), split_res(res)
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, eng.resolutions)
        return dist_lst.index(min(dist_lst))

    def update_texts(self):
        Page.update_texts(self)
        curr_lang = eng.lang_mgr.curr_lang
        self.__lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.lang_mgr.set_lang(lang_dict[arg])
        self.update_texts()


class CreditPage(Page):

    def create(self):
        self.widgets = [
            OnscreenText(text='', scale=.12, pos=(0, .4), font=self.font)]
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
            (0, 0, 0, .2), False, True, True)
        args = PageArgs(
            mdt.fsm, 'assets/fonts/zekton rg.ttf', (-3, 3, -.32, .88),
            (0, 0, 0, .2), True, False, False)
        self.main_page = MainPage(main_args)
        self.option_page = OptionPage(args)
        self.credit_page = CreditPage(args)


class _Fsm(Fsm):
    """ Definition of the DeflectorFSM Class """

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Main': ['Options', 'Credits'],
            'Options': ['Main'],
            'Credits': ['Main']}

    def enterMain(self):
        self.mdt.gui.main_page.create(self.mdt.game_fsm, self.mdt.fsm)

    def exitMain(self):
        self.mdt.gui.main_page.destroy()

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
